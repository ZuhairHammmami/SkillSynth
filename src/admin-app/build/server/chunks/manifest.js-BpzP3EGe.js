const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set([]),
	mimeTypes: {},
	_: {
		client: {start:"_app/immutable/entry/start.kKr5nk3P.js",app:"_app/immutable/entry/app.D7_wyJff.js",imports:["_app/immutable/entry/start.kKr5nk3P.js","_app/immutable/chunks/i3kxKTNh.js","_app/immutable/chunks/DStCI_bK.js","_app/immutable/chunks/DvIsU9tr.js","_app/immutable/entry/app.D7_wyJff.js","_app/immutable/chunks/DStCI_bK.js","_app/immutable/chunks/Cb1SNDBH.js","_app/immutable/chunks/DvIsU9tr.js","_app/immutable/chunks/ejTZonES.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./nodes/0.js-D2NOZk2G.js')),
			__memo(() => import('./nodes/1.js-BFm_Xufp.js')),
			__memo(() => import('./nodes/2.js-CmtJ_kLD.js')),
			__memo(() => import('./nodes/3.js-KVckkUd3.js')),
			__memo(() => import('./nodes/4.js-D2O8G_Sq.js'))
		],
		remotes: {
			
		},
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 3 },
				endpoint: null
			},
			{
				id: "/(app)/dashboard",
				pattern: /^\/dashboard\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 4 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();

export { manifest as m };
//# sourceMappingURL=manifest.js-BpzP3EGe.js.map
