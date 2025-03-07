document.addEventListener("DOMContentLoaded", async function () {
    console.log("🚀 Page loaded, initializing...");
  
    // Bestands-input (Excel)
    const excelInput = document.querySelector('input[name="config_file"]');
    if (excelInput) {
      excelInput.addEventListener("change", async () => {
        const file = excelInput.files[0];
        if (!file) return;
  
        // Direct uploaden naar /upload-excel
        const fd = new FormData();
        fd.append("excel_file", file);
  
        try {
          const resp = await fetch("/upload-excel", {
            method: "POST",
            body: fd
          });
          const result = await resp.json();
          if (result.status === "OK") {
            console.log("✅ Excel geüpload, pluginlijst opnieuw genereren...");
            await loadAvailablePlugins(); // Checkboxes updaten
          } else {
            console.error("⚠️ Fout bij /upload-excel", result);
          }
        } catch (err) {
          console.error("Fout tijdens uploadExcel fetch:", err);
        }
      });
    }
  
    // Form-element en handlers
    const installForm = document.getElementById("installForm");
    if (!installForm) {
      console.error("⚠️ installForm not found!");
      return;
    }
  
    // Initieel: Probeer pluginlijst te laden
    await loadAvailablePlugins();
  
    // Initieel: Probeer bestaande config.json te laden
    await loadPreviousConfig();
  
    // Koppel de submit-handler voor de installatie
    installForm.onsubmit = handleFormSubmit;
  });
  
  /**
   * Ophalen van de pluginlijst uit /config/available-plugins.json
   */
  async function loadAvailablePlugins() {
    try {
      console.log("🔄 Ophalen pluginlijst...");
      const resp = await fetch('/config/available-plugins.json');
      if (!resp.ok) {
        console.warn("⚠️ Geen pluginlijst gevonden (404?).");
        return;
      }
      const plugins = await resp.json();
      console.log("✅ Plugins:", plugins);
  
      const container = document.getElementById('plugin-container');
      if (!container) {
        console.warn("⚠️ Geen #plugin-container element gevonden in HTML");
        return;
      }
      container.innerHTML = "";
  
      Object.keys(plugins).forEach(category => {
        const catDiv = document.createElement('div');
        catDiv.classList.add('plugin-category');
        catDiv.innerHTML = `<h3>${category}</h3>`;
        plugins[category].forEach(plugin => {
          catDiv.innerHTML += `
            <label>
              <input type="checkbox" name="plugins" value="${plugin.url}">
              ${plugin.name} ${plugin.compatibility !== "N/A" ? `(WP ${plugin.compatibility})` : "(Premium)"}
            </label><br>
          `;
        });
        container.appendChild(catDiv);
      });
    } catch (error) {
      console.error("Fout bij loadAvailablePlugins:", error);
    }
    // Toevoegen "Alles selecteren" optie per categorie
document.querySelectorAll('.plugin-category').forEach(category => {
  const selectAll = document.createElement('input');
  selectAll.type = 'checkbox';
  selectAll.onclick = () => {
    category.querySelectorAll('input[type="checkbox"]').forEach(box => box.checked = selectAll.checked);
  };

  const label = document.createElement('label');
  label.textContent = ' Alles selecteren';
  label.prepend(selectAll);
  
  category.prepend(label);
});
  }
  
  /**
   * Ophalen van de bestaande config.json (indien aanwezig)
   */
  async function loadPreviousConfig() {
    try {
      console.log("🔄 Ophalen config.json...");
      const resp = await fetch('/config/config.json');
      if (!resp.ok) {
        console.warn("⚠️ config.json niet gevonden.");
        return;
      }
      const config = await resp.json();
      console.log("✅ Bestaande config:", config);
  
      document.getElementById('siteTitle').value = config.site_title || "";
      document.getElementById('adminUser').value = config.admin_user || "";
      document.getElementById('adminPassword').value = config.admin_password || "";
      document.getElementById('adminEmail').value = config.admin_email || "";
    } catch (error) {
      console.error("Fout bij loadPreviousConfig:", error);
    }
  }
  
  /**
   * Afhandeling van formulier-submissie: stuurt alles naar /upload-config
   */
  async function handleFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
  
    // Bepaal hostingType
    const hostingType = document.getElementById("hostingType").value;
    formData.append("hosting_type", hostingType);
  
    // Stel GraphQL endpoint op
    let graphqlEndpoint;
    if (hostingType === "hostinger") {
      graphqlEndpoint = "https://example.com/graphql";
    } else if (hostingType === "local") {
      graphqlEndpoint = "http://localhost/wordpress/graphql";
    } else {
      graphqlEndpoint = "http://localhost:8080/graphql";
    }
  
    // Geef endpoint door aan backend (/config/update-graphql)
    try {
      await fetch('/config/update-graphql', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ graphqlEndpoint })
      });
      console.log("✅ GraphQL endpoint doorgegeven.");
    } catch (err) {
      console.error("Fout bij update_graphql:", err);
    }
  
    // Stuur formulier + Excel + gekozen plugins naar /upload-config
    try {
      const resp = await fetch('/upload-config', {
        method: 'POST',
        body: formData
      });
      const result = await resp.json();
      console.log("Respons van /upload-config:", result);
      alert(result.status || "Geen status ontvangen");
    } catch (err) {
      console.error("Fout bij /upload-config:", err);
      alert("Installatie mislukt");
    }
  }
  