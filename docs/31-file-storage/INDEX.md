# SS-EDS: File Storage

## Purpose
Document the file storage strategy for SkillSynth, covering user uploads, avatar storage, resource file attachments, and project submission attachments.

## Responsibilities
- Manage user file uploads (avatars, project submissions)
- Define storage backends (local dev, S3/CDN in production)
- Handle file type validation and size limits
- Implement secure file serving with access control

## Inputs
- File upload requirements
- Storage cost considerations
- Security requirements for file access

## Outputs
- File upload API endpoints
- Storage backend configuration
- File serving middleware

## Dependencies
- 14-security (file upload security)
- 17-deployment (CDN configuration)
- 07-backend (file upload handlers)

## Sequence: File Upload Flow
```
User → Select File → Client-side Validation → POST /api/upload → Server Validation → Store File → Return URL → Save URL to DB → Display
```

## State Diagram: File Lifecycle
```
[Uploaded] → [Processed] → [Served] → [Archived] → [Deleted]
                              ↓
                        [Cache expires]
```

## Storage Strategy
| Environment | Backend | Configuration |
|-------------|---------|---------------|
| Development | Local filesystem | /uploads/ directory |
| Production | S3/CDN (future) | AWS S3 + CloudFront |
| Avatar | Local | /avatars/ directory |
| Project submissions | Local (stubbed) | /submissions/ directory |

## ERD References
- profiles: avatar URL string
- Project submissions: file URL string (when implemented)

## Rules
1. File type whitelist: images (jpg, png, webp, svg), documents (pdf, txt)
2. Max file size: 10MB per upload
3. Uploaded files must be scanned for malware (future)
4. File URLs must be served with access control
5. No direct filesystem access from frontend
6. Storage directory outside web root for security

## Examples
- Avatar upload: resized to 256×256 max, stored as WebP
- Project submission: PDF or ZIP, max 10MB

## Edge Cases
- Concurrent upload of same filename → UUID prefix ensures uniqueness
- Storage full → return 507 Insufficient Storage
- Upload interrupted → cleanup partial file

## Failure Cases
- Malicious file upload → blocked by file type and size validation
- Storage backend unreachable → temporary local fallback
- CDN cache miss → serve from origin, slower

## Recovery Procedures
1. Check storage directory permissions
2. Verify file type validation logic
3. Clear CDN cache for stale files

## Refactoring Strategy
- Implement S3-compatible storage for production
- Add file processing pipeline (resize, compress)
- Implement file versioning for overwrites
- Add signed URL generation for secure file access
