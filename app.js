// Tailwind CSS Configuration
tailwind.config = {
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                background: '#09090b', // Deep Zinc
                primary: '#10b981',    // Emerald (statt Blau)
                panel: '#18181b',      // zinc-900
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
    
    // Checkbox Validation for Checkout
    const checkboxes = document.querySelectorAll('.legal-checkbox');
    const buyBtn = document.getElementById('buy-btn');
    
    if (checkboxes.length > 0 && buyBtn) {
        const validateCheckboxes = () => {
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);
            buyBtn.disabled = !allChecked;
        };
        
        checkboxes.forEach(cb => {
            cb.addEventListener('change', validateCheckboxes);
        });
    }
    
    // Wir implementieren die Undo-Redo Funktionalitaet oder State-Mutationen später, 
    // aber als Vorbereitung für die Undo-Regel hier ein Platzhalter:
    // function pushUndo(state) { ... }
});
