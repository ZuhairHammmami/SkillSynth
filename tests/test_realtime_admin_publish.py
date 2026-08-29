"""Admin SSE publish tests — send_admin_event/send_admin_activity frames,
the named-event wire format, and the broadcast call sites (Task 4).

Covers publisher unit behavior, that admin_generator frames carry an
`event:` field (the admin sse.ts addEventListener subscription needs it),
and that path_generated / assessment_completed / activity rows now also
enqueue an admin frame WITHOUT touching the per-user send_event path.
"""

import asyncio
import uuid

from backend.entities.identity import User
from backend.events import publisher
from backend.services import auth_service


def _fresh(email):
    """Unique address so registered learners never collide with seeds."""
    return f"{email}_{uuid.uuid4().hex[:8]}@test.com"


def _register_and_login(api_client, email):
    """Register + login a fresh learner; returns bearer headers."""
    api_client.post("/api/auth/register", json={
        "email": email, "password": "CastPass@123"})
    token = api_client.post("/api/auth/token", data={
        "username": email, "password": "CastPass@123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestSendAdminEvent:
    """Unit pins on the pub/sub primitive in events/publisher.py."""

    def test_enqueues_a_frame_to_every_queue(self):
        q1 = asyncio.Queue()
        q2 = asyncio.Queue()
        publisher.admin_event_clients.extend([q1, q2])
        try:
            publisher.send_admin_event("path_generated", {"path_id": 1})
            for q in (q1, q2):
                assert q.get_nowait() == {"type": "path_generated",
                                          "path_id": 1}
        finally:
            publisher.admin_event_clients.clear()

    def test_swallows_queue_full(self):
        q = asyncio.Queue(maxsize=1)
        q.put_nowait({})
        publisher.admin_event_clients.append(q)
        try:
            publisher.send_admin_event("activity", {"id": 1})
        finally:
            publisher.admin_event_clients.clear()

    def test_no_op_without_clients(self):
        publisher.admin_event_clients.clear()
        publisher.send_admin_event("path_generated", {"path_id": 1})


class TestAdminGeneratorWireFormat:
    """Admin generator frames must be named SSE events (`event: <type>`)
    so the admin app's `addEventListener('<type>', ...)` actually fires."""

    def test_generator_emits_named_event_frames(self):
        async def run():
            before = list(publisher.admin_event_clients)
            gen = publisher.admin_event_generator()
            frames = [await anext(gen)]
            queue = publisher.admin_event_clients[-1]
            assert queue not in before
            queue.put_nowait({"type": "activity", "id": 7})
            frames.append(await anext(gen))
            await gen.aclose()
            return frames
        frames = asyncio.run(run())
        assert frames[0] == 'event: connected\ndata: {"type": "connected"}\n\n'
        assert frames[1].startswith("event: activity\ndata: ")
        assert '"id": 7' in frames[1]
        assert publisher.admin_event_clients == []


class TestBroadcastCallSites:
    """The router broadcast additions keep the per-user send_event call
    and add an equivalent admin-channel frame."""

    def test_path_generated_broadcasts_admin_and_user(
            self, api_client, monkeypatch):
        import backend.routers.paths as paths_router
        user_frames, admin_frames = [], []
        monkeypatch.setattr(
            paths_router, "send_event",
            lambda uid, t, d=None: user_frames.append((uid, t, d)))
        monkeypatch.setattr(
            paths_router, "send_admin_event",
            lambda t, d=None: admin_frames.append((t, d)))
        headers = _register_and_login(api_client,
                                      _fresh("pathcast"))
        res = api_client.post("/api/generate-path/", json={
            "goal": "Data Scientist", "weekly_hours": 10,
            "preferences": {}, "answers": {}}, headers=headers)
        assert res.status_code == 200, res.text
        path_id = res.json()["id"]
        assert len(user_frames) == 1
        assert user_frames[0][1] == "path_generated"
        assert user_frames[0][2]["path_id"] == path_id
        assert admin_frames[0][0] == "path_generated"
        assert admin_frames[0][1]["path_id"] == path_id

    def test_assessment_completed_broadcasts_admin_and_user(
            self, api_client, auth_headers, admin_headers, monkeypatch):
        import backend.routers.assessments as asc_router
        user_frames, admin_frames = [], []
        monkeypatch.setattr(
            asc_router, "send_event",
            lambda uid, t, d=None: user_frames.append((uid, t, d)))
        monkeypatch.setattr(
            asc_router, "send_admin_event",
            lambda t, d=None: admin_frames.append((t, d)))
        assessments = api_client.get("/api/admin/assessments",
                                     headers=admin_headers).json()
        html = next(a for a in assessments
                    if a["title"] == "HTML Assessment")
        res = api_client.post("/api/assessments/submit", json={
            "assessment_id": html["id"], "answers": [0, 1, 0, 0, 0]},
            headers=auth_headers)
        assert res.status_code == 200, res.text
        assert user_frames and user_frames[0][1] == "assessment_completed"
        kind, payload = admin_frames[0]
        assert kind == "assessment_completed"
        assert payload == {"assessment_id": html["id"],
                           "score": 100, "total_questions": 5}


class TestActivityBroadcast:
    """An audit write feeds the admin activity channel via the shared
    send_admin_activity helper at the auth call site."""

    def test_log_auth_emits_activity_admin_frame(self, db_session, monkeypatch):
        sent = []
        monkeypatch.setattr(
            publisher, "send_admin_event",
            lambda t, d=None: sent.append((t, d)))
        uid = db_session.query(User).filter_by(
            email="veteran@skillsynth.io").one().id
        auth_service.log_auth(db_session, uid, "veteran@skillsynth.io",
                              True, "127.0.0.1")
        assert len(sent) == 1
        kind, frame = sent[0]
        assert kind == "activity"
        assert frame["category"] == "auth"
        assert frame["action"] == "login"
        assert frame["user_id"] == uid
        assert frame["entity_type"] == "user"
        assert frame["entity_id"] == uid
        assert frame["data"] == {"email": "veteran@skillsynth.io",
                                 "success": True}
        assert frame["created_at"]