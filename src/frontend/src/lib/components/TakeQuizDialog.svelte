<!-- AI practice-test launcher. Degrades gracefully when AI is disabled (503). -->
<script lang="ts">
  import { apiFetch, ApiError } from '$lib/api/client';
  import Panel from '$lib/components/ui/Panel.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Dialog from '$lib/components/ui/Dialog.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Field from '$lib/components/ui/Field.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import { error as toastError, info, success } from '$lib/components/ui/toast';
  import { t } from '$lib/i18n';

  let { open = $bindable(false), skills = [] }: { open?: boolean; skills?: { id: number; name: string }[] } = $props();
  let skillId = $state<number | null>(null);
  let n = $state(5);
  let busy = $state(false);

  $effect(() => { if (skills.length && skillId == null) skillId = skills[0].id; });

  async function start() {
    if (skillId == null) return;
    busy = true;
    try {
      await apiFetch('/ai/tests/generate', { method: 'POST', body: { skill_id: skillId, n_questions: n } });
      success(t('wizard.assessmentQueued'));
      open = false;
    } catch (e) {
      if (e instanceof ApiError && e.status === 503) {
        info('AI features are currently disabled');
      } else {
        toastError(e instanceof ApiError ? e.detail : 'Request failed');
      }
      open = false;
    } finally {
      busy = false;
    }
  }
</script>

<Dialog bind:open title={t('wizard.assessmentTitle')}>
  <Field label={t('wizard.summaryGoal')}>
    <Select bind:value={skillId} options={skills.map((s) => ({ value: s.id, label: s.name }))} />
  </Field>
  <Field label={t('wizard.questionLabel')}>
    <Select bind:value={n} options={[3, 5, 10].map((x) => ({ value: x, label: String(x) }))} />
  </Field>
  {#snippet footer()}
    <Button variant="ghost" onclick={() => (open = false)}>{t('common.cancel')}</Button>
    <Button onclick={start} disabled={busy}>{#if busy}<Spinner />{:else}{t('wizard.startAssessment')}{/if}</Button>
  {/snippet}
</Dialog>
