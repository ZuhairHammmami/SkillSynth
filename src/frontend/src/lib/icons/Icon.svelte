<!-- Hand-drawn-style SVG icon set. Replaces lucide-react. One component, many
     named glyphs, drawn with warm 1.6 stroke so they read as crafted, not stock. -->
<script lang="ts">
  export let name: string;
  export let size = 20;
  export let stroke = 1.6;

  const paths: Record<string, string> = {
    dashboard: 'M3 3h7v8H3zM14 3h7v5h-7zM14 11h7v10h-7zM3 13h7v8H3z',
    learn: 'M4 5.5A2 2 0 0 1 6 4h9a2 2 0 0 1 2 2v11a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2zM6 4v14',
    analytics: 'M4 20V10M10 20V4M16 20v-7M22 20H2',
    profile: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21a8 8 0 0 1 16 0',
    settings: 'M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6zM4 12l1.5-1 1 2-1.5 1M20 12l-1.5-1-1 2 1.5 1M12 4l-1 1.5 2 1 1-1.5M12 20l-1-1.5 2-1 1 1.5',
    plus: 'M12 5v14M5 12h14',
    trash: 'M5 7h14M9 7V4h6v3M7 7l1 13h8l1-13',
    edit: 'M4 20l4-1 11-11-3-3L5 16zM14 6l3 3',
    check: 'M5 12l5 5L20 6',
    chevron: 'M9 6l6 6-6 6',
    globe: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18',
    logout: 'M14 4h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-4M10 12H3M6 8l-4 4 4 4',
    sparkles: 'M12 4l1.6 4.4L18 10l-4.4 1.6L12 16l-1.6-4.4L6 10l4.4-1.6zM18 15l.8 2.2L21 18l-2.2.8L18 21l-.8-2.2L15 18l2.2-.8z',
    search: 'M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM20 20l-4-4',
    menu: 'M4 7h16M4 12h16M4 17h16',
    x: 'M6 6l12 12M18 6L6 18',
    download: 'M12 4v10M8 11l4 3 4-3M5 20h14',
    alert: 'M12 4l9 16H3zM12 10v5M12 17.5v.5',
    key: 'M14 7a4 4 0 1 0-3.5 6.9L5 20v-3l1-1 2 2 1-1-2-2h3l3.5-3.5A4 4 0 0 0 14 7z',
    shield: 'M12 3l7 3v6c0 4-3 7-7 9-4-2-7-5-7-9V6z',
    database: 'M12 3c4 0 7 1 7 3s-3 3-7 3-7-1-7-3 3-3 7-3zM5 6v6c0 2 3 3 7 3s7-1 7-3V6M5 12v6c0 2 3 3 7 3s7-1 7-3v-6',
    activity: 'M3 12h4l3-8 4 16 3-8h4',
    refresh: 'M20 11a8 8 0 0 0-14-4M4 5v3h3M4 13a8 8 0 0 0 14 4M20 19v-3h-3',
    layers: 'M12 3l9 5-9 5-9-5zM3 13l9 5 9-5',
    flag: 'M5 21V4h12l-2 4 2 4H5',
    calendar: 'M4 7a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1zM4 10h16M8 4v4M16 4v4',
    arrow: 'M5 12h14M13 6l6 6-6 6',
    users: 'M9 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM3 20a6 6 0 0 1 12 0M16 11a3 3 0 0 0 0-6M15 14a6 6 0 0 1 6 6',
    category: 'M4 5h7v7H4zM13 5h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z',
    resource: 'M4 5h16v14H4zM8 9h8M8 13h8M8 17h5',
    role: 'M12 3v4M8 7h8M6 21v-7a6 6 0 0 1 12 0v7',
    quiz: 'M9 9a3 3 0 1 1 4 2.8L9 16M9 16h.01M14 14h.01',
    brain: 'M9 4a3 3 0 0 0-3 3 3 3 0 0 0-1 5 3 3 0 0 0 2 4 3 3 0 0 0 5 1V4a3 3 0 0 0-3 0zM15 4a3 3 0 0 1 3 3 3 3 0 0 1 1 5 3 3 0 0 1-2 4 3 3 0 0 1-5 1',
    book: 'M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 0-3 3zM5 4v16',
    trending: 'M3 17l6-6 4 4 8-8M21 7h-5M21 7v5',
    clock: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 7v5l4 2',
    mail: 'M3 6h18v12H3zM3 7l9 6 9-6',
    home: 'M4 11l8-7 8 7M6 10v9h12v-9',
    sprout: 'M12 20v-7M12 13c-5-1-8-5-8-9 5 0 8 4 8 9zM12 11c4-2 7 0 8 4-4 2-8 0-8-4z',
    info: 'M12 8h.01M11 12h1v5h1M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z',
    star: 'M12 3l2.6 5.6L20 9.3l-4 4 1 6-5-2.8L7 19.3l1-6-4-4 5.4-.7z',
    external: 'M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5'
  };
</script>

<svg
  xmlns="http://www.w3.org/2000/svg"
  width={size}
  height={size}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width={stroke}
  stroke-linecap="round"
  stroke-linejoin="round"
  aria-hidden="true"
>
  <path d={paths[name] ?? paths.arrow} />
</svg>
