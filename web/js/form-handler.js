// form-handler.js: Laadt plugins dynamisch uit available-plugins.json in het formulier
// en controleert op compatibiliteit met de huidige WordPress versie

window.onload = async function() {
    try {
        // Haal de huidige WordPress versie op via de API
        const wpResponse = await fetch('/config/wp-version');
        const wpVersion = await wpResponse.json();
        const currentWpVersion = wpVersion.version;
        console.log(`Huidige WordPress versie: ${currentWpVersion}`);

        // Haal de pluginlijst op en filter op compatibiliteit
        const pluginResponse = await fetch('/config/available-plugins.json');
        if (!pluginResponse.ok) {
            console.error("Kan available-plugins.json niet laden.");
            return;
        }

        const plugins = await pluginResponse.json();
        const container = document.getElementById('plugin-container');

        // Haal reeds geselecteerde plugins op uit config.json (indien beschikbaar)
        const configResponse = await fetch('/config/config.json');
        let selectedPlugins = [];
        if (configResponse.ok) {
            const config = await configResponse.json();
            selectedPlugins = config.external_plugins || [];
        }

        // Groepeer plugins per categorie en voeg ze toe aan het formulier
        Object.keys(plugins).forEach(category => {
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'plugin-category';
            categoryDiv.innerHTML = `<h3>${category}</h3>`;

            plugins[category].forEach(plugin => {
                const isChecked = selectedPlugins.includes(plugin.url) ? 'checked' : '';

                if (isCompatible(currentWpVersion, plugin.compatibility)) {
                    categoryDiv.innerHTML += `
                        <label>
                            <input type="checkbox" name="plugins" value="${plugin.url}" ${isChecked}>
                            ${plugin.name} (Compatibel met WP ${plugin.compatibility})
                        </label><br>
                    `;
                } else {
                    categoryDiv.innerHTML += `
                        <label style="color: red;">
                            ❌ ${plugin.name} (Niet compatibel met WP ${currentWpVersion})
                        </label><br>
                    `;
                }
            });

            container.appendChild(categoryDiv);
        });

        console.log("✅ Pluginlijst succesvol geladen.");
    } catch (error) {
        console.error("Fout bij het laden van plugins: ", error);
    }
};

// Controleer of de plugin compatibel is met de huidige WordPress versie
function isCompatible(currentVersion, compatibilityRange) {
    const [minVersion, maxVersion] = compatibilityRange.split(' - ').map(v => parseFloat(v));
    const wpVersion = parseFloat(currentVersion);
    return wpVersion >= minVersion && wpVersion <= maxVersion;
}
