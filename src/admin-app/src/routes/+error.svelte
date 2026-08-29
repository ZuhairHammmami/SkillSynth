<!-- Admin error boundary. -->
<script lang="ts">
  import { page } from '$app/stores';
  import Illustration from '$lib/components/Illustration.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { t } from '$lib/i18n';
</script>

<div class="wrap">
  <Illustration name="sprout" width={140} />
  <h1>{$page.status}</h1>
  <p class="muted">{$page.error?.message || t('error.description')}</p>
  <Button onclick={() => history.back()}>{t('common.back')}</Button>
</div>

<style>
  .wrap { min-height: 70vh; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.8rem; text-align: center; padding: 2rem; }
  h1 { font-size: 3rem; margin: 0; }
</style>
