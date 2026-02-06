// Use relative path for production (Render serves both front and back)
const API_URL = "";

async function login() {
    const usernameInput = document.getElementById('username-input');
    const username = usernameInput.value.trim();

    if (!username) {
        alert("Por favor ingresa un usuario");
        return;
    }

    // Simulate Loading
    const btn = document.querySelector('button');
    const originalText = btn.innerText;
    btn.innerText = "Conectando con el Motor...";
    btn.disabled = true;

    try {
        // Real GET endpoint call
        const response = await fetch(`${API_URL}/api/users/${username}`);

        if (!response.ok) {
            if (response.status === 404) {
                alert("Usuario no encontrado ¿Ya interactuaste con el bot?");
                // Optionally call onboarding here automatically, but better to warn.
            } else {
                throw new Error("Error en el servidor");
            }
            btn.innerText = originalText;
            btn.disabled = false;
            return;
        }

        const data = await response.json();

        // Update UI
        document.getElementById('login-section').classList.add('hidden');
        document.getElementById('dashboard-section').classList.remove('hidden');
        // Tailwind flex reset
        document.getElementById('dashboard-section').style.display = 'flex';
        document.getElementById('dashboard-section').classList.add('flex-col');

        document.getElementById('user-name').innerText = `Hola, @${data.instagram_username}`;
        document.getElementById('user-rank').innerHTML =
            `<span class="inline-block w-2 h-2 rounded-full bg-gold animate-pulse"></span> Rango: ${data.rank}`;

        document.getElementById('user-score').innerText = data.loyalty_score;


        // Update Progress Bar
        const progressEl = document.querySelector('.overflow-hidden > div');
        if (progressEl) {
            progressEl.style.width = `${data.progress_percent}%`;
            progressEl.innerText = `${data.progress_percent}%`;
        }

        // LOAD MISSIONS
        loadMissions();

    } catch (error) {
        console.error(error);
        alert("Error al conectar. Asegúrate de que el servidor backend esté corriendo (main.py).");
        btn.innerText = originalText;
        btn.disabled = false;
    }
}

async function loadMissions() {
    try {
        const res = await fetch(`${API_URL}/api/users/missions/active`);
        if (!res.ok) return;
        const missions = await res.json();

        const container = document.getElementById('missions-container');
        if (!container) return;

        container.innerHTML = ''; // Clear hardcoded

        missions.forEach(m => {
            const el = document.createElement('div');
            el.className = "bg-dark/40 p-3 rounded-lg hover:bg-dark/60 transition-colors cursor-pointer group border border-transparent hover:border-accent/30";
            el.innerHTML = `
                <div class="flex justify-between items-start">
                    <div>
                        <h4 class="font-bold text-sm group-hover:text-accent transition-colors">${m.title}</h4>
                        <p class="text-xs text-gray-400">Categoría: ${m.category}</p>
                    </div>
                    <span class="text-xs font-bold text-gold">+${m.points} pts</span>
                </div>
            `;
            // Optional: Add click handler if link exists
            if (m.link && m.link !== "#") {
                el.onclick = () => window.open(m.link, '_blank');
            }
            container.appendChild(el);
        });

    } catch (e) {
        console.error("Error loading missions", e);
    }
}
