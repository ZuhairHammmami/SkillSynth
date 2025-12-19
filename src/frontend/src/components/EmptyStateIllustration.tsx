// المسار: src/frontend/src/app/components/EmptyStateIllustration.tsx
export const EmptyStateIllustration = () => (
    <svg width="200" height="160" viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="10" y="30" width="180" height="120" rx="8" fill="hsl(var(--muted))" />
        <rect x="25" y="50" width="150" height="10" rx="5" fill="hsl(var(--border))" />
        <rect x="25" y="70" width="100" height="10" rx="5" fill="hsl(var(--border))" />
        <circle cx="155" cy="115" r="20" fill="hsl(var(--primary))" fillOpacity="0.1" />
        <path d="M145 115 L155 125 L165 105" stroke="hsl(var(--primary))" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M50 0 L 70 20 L30 20 Z" fill="hsl(var(--secondary))" fillOpacity="0.2"/>
        <circle cx="170" cy="20" r="10" fill="hsl(var(--primary))" fillOpacity="0.2"/>
    </svg>
);