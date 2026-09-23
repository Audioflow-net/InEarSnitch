// Tailwind CSS Configuration
tailwind.config = {
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                background: '#09090b', // Deep Zinc
                primary: '#3b82f6',    // Blue
                success: '#10b981',    // Emerald
                panel: '#18181b',      // zinc-900 for slightly lighter panels
                border: '#27272a',     // zinc-800
            },
            fontFamily: {
                mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
                sans: ['"Inter"', 'ui-sans-serif', 'system-ui', '-apple-system', 'sans-serif'],
            }
        }
    }
}

// InEar Snitch Application Logic
document.addEventListener('DOMContentLoaded', () => {
    console.log("InEar Snitch - Metrology Lab Initialized");
    
    // Wir implementieren die Undo-Redo Funktionalitaet oder State-Mutationen später, 
    // aber als Vorbereitung für die Undo-Regel hier ein Platzhalter:
    // function pushUndo(state) { ... }
});
