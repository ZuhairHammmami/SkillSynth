<!-- Inline spinner used by buttons and loading states. Decorative but announced
     as a status region for assistive tech. -->
<div class="spinner" role="status" aria-label="Loading"></div>

<style>
  .spinner {
    width: 1.4rem; height: 1.4rem; border-radius: 50%;
    border: 2px solid var(--line-strong);
    border-top-color: var(--accent);
    display: inline-block;
    animation: spin 0.7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
