
// this file is generated — do not edit it


/// <reference types="@sveltejs/kit" />

/**
 * This module provides access to environment variables that are injected _statically_ into your bundle at build time and are limited to _private_ access.
 * 
 * |         | Runtime                                                                    | Build time                                                               |
 * | ------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
 * | Private | [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private) | [`$env/static/private`](https://svelte.dev/docs/kit/$env-static-private) |
 * | Public  | [`$env/dynamic/public`](https://svelte.dev/docs/kit/$env-dynamic-public)   | [`$env/static/public`](https://svelte.dev/docs/kit/$env-static-public)   |
 * 
 * Static environment variables are [loaded by Vite](https://vitejs.dev/guide/env-and-mode.html#env-files) from `.env` files and `process.env` at build time and then statically injected into your bundle at build time, enabling optimisations like dead code elimination.
 * 
 * **_Private_ access:**
 * 
 * - This module cannot be imported into client-side code
 * - This module only includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://svelte.dev/docs/kit/configuration#env) (if configured)
 * 
 * For example, given the following build time environment:
 * 
 * ```env
 * ENVIRONMENT=production
 * PUBLIC_BASE_URL=http://site.com
 * ```
 * 
 * With the default `publicPrefix` and `privatePrefix`:
 * 
 * ```ts
 * import { ENVIRONMENT, PUBLIC_BASE_URL } from '$env/static/private';
 * 
 * console.log(ENVIRONMENT); // => "production"
 * console.log(PUBLIC_BASE_URL); // => throws error during build
 * ```
 * 
 * The above values will be the same _even if_ different values for `ENVIRONMENT` or `PUBLIC_BASE_URL` are set at runtime, as they are statically replaced in your code with their build time values.
 */
declare module '$env/static/private' {
	export const NEXT_PUBLIC_API_BASE_URL: string;
	export const SVELTEKIT_FORK: string;
	export const NODE_ENV: string;
	export const KITTY_INSTALLATION_DIR: string;
	export const XKB_DEFAULT_OPTIONS: string;
	export const MAIL: string;
	export const KDE_APPLICATIONS_AS_SCOPE: string;
	export const DBUS_SESSION_BUS_ADDRESS: string;
	export const _JAVA_AWT_WM_NONREPARENTING: string;
	export const LANG: string;
	export const GTK2_RC_FILES: string;
	export const PWD: string;
	export const KITTY_PUBLIC_KEY: string;
	export const XAUTHORITY: string;
	export const XDG_SESSION_TYPE: string;
	export const HOME: string;
	export const XDG_SEAT: string;
	export const JOURNAL_STREAM: string;
	export const TERMINFO: string;
	export const SYSTEMD_EXEC_PID: string;
	export const SESSION_MANAGER: string;
	export const OPENCODE: string;
	export const PAM_KWALLET5_LOGIN: string;
	export const COLORTERM: string;
	export const PATH: string;
	export const KDE_SESSION_UID: string;
	export const ICEAUTHORITY: string;
	export const XDG_SESSION_DESKTOP: string;
	export const MEMORY_PRESSURE_WRITE: string;
	export const INVOCATION_ID: string;
	export const SHELL: string;
	export const VSSCRIPT_PATH: string;
	export const LOGNAME: string;
	export const KITTY_PID: string;
	export const NODE_PATH: string;
	export const QT_WAYLAND_RECONNECT: string;
	export const GTK_RC_FILES: string;
	export const XDG_CURRENT_DESKTOP: string;
	export const AGENT: string;
	export const XDG_VTNR: string;
	export const MEMORY_PRESSURE_WATCH: string;
	export const MOTD_SHOWN: string;
	export const STARSHIP_SHELL: string;
	export const XDG_SESSION_PATH: string;
	export const KITTY_WINDOW_ID: string;
	export const WAYLAND_DISPLAY: string;
	export const XDG_SEAT_PATH: string;
	export const MANAGERPID: string;
	export const STARSHIP_SESSION_KEY: string;
	export const DISPLAY: string;
	export const MANAGERPIDFDID: string;
	export const XDG_MENU_PREFIX: string;
	export const XKB_DEFAULT_LAYOUT: string;
	export const XKB_DEFAULT_MODEL: string;
	export const XDG_SESSION_CLASS: string;
	export const XDG_CONFIG_DIRS: string;
	export const TERM: string;
	export const OPENCODE_PID: string;
	export const USER: string;
	export const XDG_DATA_DIRS: string;
	export const KDE_SESSION_VERSION: string;
	export const SHLVL: string;
	export const LC_TELEPHONE: string;
	export const XDG_SESSION_ID: string;
	export const XDG_RUNTIME_DIR: string;
	export const DEBUGINFOD_URLS: string;
	export const DESKTOP_SESSION: string;
	export const KDE_FULL_SESSION: string;
}

/**
 * This module provides access to environment variables that are injected _statically_ into your bundle at build time and are _publicly_ accessible.
 * 
 * |         | Runtime                                                                    | Build time                                                               |
 * | ------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
 * | Private | [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private) | [`$env/static/private`](https://svelte.dev/docs/kit/$env-static-private) |
 * | Public  | [`$env/dynamic/public`](https://svelte.dev/docs/kit/$env-dynamic-public)   | [`$env/static/public`](https://svelte.dev/docs/kit/$env-static-public)   |
 * 
 * Static environment variables are [loaded by Vite](https://vitejs.dev/guide/env-and-mode.html#env-files) from `.env` files and `process.env` at build time and then statically injected into your bundle at build time, enabling optimisations like dead code elimination.
 * 
 * **_Public_ access:**
 * 
 * - This module _can_ be imported into client-side code
 * - **Only** variables that begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) (which defaults to `PUBLIC_`) are included
 * 
 * For example, given the following build time environment:
 * 
 * ```env
 * ENVIRONMENT=production
 * PUBLIC_BASE_URL=http://site.com
 * ```
 * 
 * With the default `publicPrefix` and `privatePrefix`:
 * 
 * ```ts
 * import { ENVIRONMENT, PUBLIC_BASE_URL } from '$env/static/public';
 * 
 * console.log(ENVIRONMENT); // => throws error during build
 * console.log(PUBLIC_BASE_URL); // => "http://site.com"
 * ```
 * 
 * The above values will be the same _even if_ different values for `ENVIRONMENT` or `PUBLIC_BASE_URL` are set at runtime, as they are statically replaced in your code with their build time values.
 */
declare module '$env/static/public' {
	export const PUBLIC_API_BASE_URL: string;
}

/**
 * This module provides access to environment variables set _dynamically_ at runtime and that are limited to _private_ access.
 * 
 * |         | Runtime                                                                    | Build time                                                               |
 * | ------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
 * | Private | [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private) | [`$env/static/private`](https://svelte.dev/docs/kit/$env-static-private) |
 * | Public  | [`$env/dynamic/public`](https://svelte.dev/docs/kit/$env-dynamic-public)   | [`$env/static/public`](https://svelte.dev/docs/kit/$env-static-public)   |
 * 
 * Dynamic environment variables are defined by the platform you're running on. For example if you're using [`adapter-node`](https://github.com/sveltejs/kit/tree/main/packages/adapter-node) (or running [`vite preview`](https://svelte.dev/docs/kit/cli)), this is equivalent to `process.env`.
 * 
 * **_Private_ access:**
 * 
 * - This module cannot be imported into client-side code
 * - This module includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://svelte.dev/docs/kit/configuration#env) (if configured)
 * 
 * > [!NOTE] In `dev`, `$env/dynamic` includes environment variables from `.env`. In `prod`, this behavior will depend on your adapter.
 * 
 * > [!NOTE] To get correct types, environment variables referenced in your code should be declared (for example in an `.env` file), even if they don't have a value until the app is deployed:
 * >
 * > ```env
 * > MY_FEATURE_FLAG=
 * > ```
 * >
 * > You can override `.env` values from the command line like so:
 * >
 * > ```sh
 * > MY_FEATURE_FLAG="enabled" npm run dev
 * > ```
 * 
 * For example, given the following runtime environment:
 * 
 * ```env
 * ENVIRONMENT=production
 * PUBLIC_BASE_URL=http://site.com
 * ```
 * 
 * With the default `publicPrefix` and `privatePrefix`:
 * 
 * ```ts
 * import { env } from '$env/dynamic/private';
 * 
 * console.log(env.ENVIRONMENT); // => "production"
 * console.log(env.PUBLIC_BASE_URL); // => undefined
 * ```
 */
declare module '$env/dynamic/private' {
	export const env: {
		NEXT_PUBLIC_API_BASE_URL: string;
		SVELTEKIT_FORK: string;
		NODE_ENV: string;
		KITTY_INSTALLATION_DIR: string;
		XKB_DEFAULT_OPTIONS: string;
		MAIL: string;
		KDE_APPLICATIONS_AS_SCOPE: string;
		DBUS_SESSION_BUS_ADDRESS: string;
		_JAVA_AWT_WM_NONREPARENTING: string;
		LANG: string;
		GTK2_RC_FILES: string;
		PWD: string;
		KITTY_PUBLIC_KEY: string;
		XAUTHORITY: string;
		XDG_SESSION_TYPE: string;
		HOME: string;
		XDG_SEAT: string;
		JOURNAL_STREAM: string;
		TERMINFO: string;
		SYSTEMD_EXEC_PID: string;
		SESSION_MANAGER: string;
		OPENCODE: string;
		PAM_KWALLET5_LOGIN: string;
		COLORTERM: string;
		PATH: string;
		KDE_SESSION_UID: string;
		ICEAUTHORITY: string;
		XDG_SESSION_DESKTOP: string;
		MEMORY_PRESSURE_WRITE: string;
		INVOCATION_ID: string;
		SHELL: string;
		VSSCRIPT_PATH: string;
		LOGNAME: string;
		KITTY_PID: string;
		NODE_PATH: string;
		QT_WAYLAND_RECONNECT: string;
		GTK_RC_FILES: string;
		XDG_CURRENT_DESKTOP: string;
		AGENT: string;
		XDG_VTNR: string;
		MEMORY_PRESSURE_WATCH: string;
		MOTD_SHOWN: string;
		STARSHIP_SHELL: string;
		XDG_SESSION_PATH: string;
		KITTY_WINDOW_ID: string;
		WAYLAND_DISPLAY: string;
		XDG_SEAT_PATH: string;
		MANAGERPID: string;
		STARSHIP_SESSION_KEY: string;
		DISPLAY: string;
		MANAGERPIDFDID: string;
		XDG_MENU_PREFIX: string;
		XKB_DEFAULT_LAYOUT: string;
		XKB_DEFAULT_MODEL: string;
		XDG_SESSION_CLASS: string;
		XDG_CONFIG_DIRS: string;
		TERM: string;
		OPENCODE_PID: string;
		USER: string;
		XDG_DATA_DIRS: string;
		KDE_SESSION_VERSION: string;
		SHLVL: string;
		LC_TELEPHONE: string;
		XDG_SESSION_ID: string;
		XDG_RUNTIME_DIR: string;
		DEBUGINFOD_URLS: string;
		DESKTOP_SESSION: string;
		KDE_FULL_SESSION: string;
		[key: `PUBLIC_${string}`]: undefined;
		[key: `${string}`]: string | undefined;
	}
}

/**
 * This module provides access to environment variables set _dynamically_ at runtime and that are _publicly_ accessible.
 * 
 * |         | Runtime                                                                    | Build time                                                               |
 * | ------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
 * | Private | [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private) | [`$env/static/private`](https://svelte.dev/docs/kit/$env-static-private) |
 * | Public  | [`$env/dynamic/public`](https://svelte.dev/docs/kit/$env-dynamic-public)   | [`$env/static/public`](https://svelte.dev/docs/kit/$env-static-public)   |
 * 
 * Dynamic environment variables are defined by the platform you're running on. For example if you're using [`adapter-node`](https://github.com/sveltejs/kit/tree/main/packages/adapter-node) (or running [`vite preview`](https://svelte.dev/docs/kit/cli)), this is equivalent to `process.env`.
 * 
 * **_Public_ access:**
 * 
 * - This module _can_ be imported into client-side code
 * - **Only** variables that begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) (which defaults to `PUBLIC_`) are included
 * 
 * > [!NOTE] In `dev`, `$env/dynamic` includes environment variables from `.env`. In `prod`, this behavior will depend on your adapter.
 * 
 * > [!NOTE] To get correct types, environment variables referenced in your code should be declared (for example in an `.env` file), even if they don't have a value until the app is deployed:
 * >
 * > ```env
 * > MY_FEATURE_FLAG=
 * > ```
 * >
 * > You can override `.env` values from the command line like so:
 * >
 * > ```sh
 * > MY_FEATURE_FLAG="enabled" npm run dev
 * > ```
 * 
 * For example, given the following runtime environment:
 * 
 * ```env
 * ENVIRONMENT=production
 * PUBLIC_BASE_URL=http://example.com
 * ```
 * 
 * With the default `publicPrefix` and `privatePrefix`:
 * 
 * ```ts
 * import { env } from '$env/dynamic/public';
 * console.log(env.ENVIRONMENT); // => undefined, not public
 * console.log(env.PUBLIC_BASE_URL); // => "http://example.com"
 * ```
 * 
 * ```
 * 
 * ```
 */
declare module '$env/dynamic/public' {
	export const env: {
		PUBLIC_API_BASE_URL: string;
		[key: `PUBLIC_${string}`]: string | undefined;
	}
}
