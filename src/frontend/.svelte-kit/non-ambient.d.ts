
// this file is generated — do not edit it


declare module "svelte/elements" {
	export interface HTMLAttributes<T> {
		'data-sveltekit-keepfocus'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-noscroll'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-preload-code'?:
			| true
			| ''
			| 'eager'
			| 'viewport'
			| 'hover'
			| 'tap'
			| 'off'
			| undefined
			| null;
		'data-sveltekit-preload-data'?: true | '' | 'hover' | 'tap' | 'off' | undefined | null;
		'data-sveltekit-reload'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-replacestate'?: true | '' | 'off' | undefined | null;
	}
}

export {};


declare module "$app/types" {
	type MatcherParam<M> = M extends (param : string) => param is (infer U extends string) ? U : string;

	export interface AppTypes {
		RouteId(): "/(auth)" | "/(app)" | "/" | "/(app)/dashboard" | "/(auth)/forgot-password" | "/(auth)/login" | "/(auth)/register" | "/(auth)/reset-password";
		RouteParams(): {
			
		};
		LayoutParams(): {
			"/(auth)": Record<string, never>;
			"/(app)": Record<string, never>;
			"/": Record<string, never>;
			"/(app)/dashboard": Record<string, never>;
			"/(auth)/forgot-password": Record<string, never>;
			"/(auth)/login": Record<string, never>;
			"/(auth)/register": Record<string, never>;
			"/(auth)/reset-password": Record<string, never>
		};
		Pathname(): "/" | "/dashboard" | "/forgot-password" | "/login" | "/register" | "/reset-password";
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): "/favicon.svg" | string & {};
	}
}