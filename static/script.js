// Aquí puedes agregar scripts adicionales si necesitas funcionalidades extra.
// script.js
document.addEventListener("DOMContentLoaded", () => {
    const uploadButton = document.getElementById("upload-button");
    const procesarButton = document.getElementById("procesar-button");
    const guardarButton = document.getElementById("guardar-button");
    const progressBar = document.getElementById("progress-bar");
    const progressText = document.getElementById("progress-text");
    const tablaEditable = document.getElementById("tabla-editable");
    const mapaContainer = document.getElementById("mapa-container");

    let mapa;
    let markers = [];

    // Inicializar el mapa
    function initMap() {
        mapa = new google.maps.Map(document.getElementById("map"), {
            center: { lat: 20.659698, lng: -103.349609 },
            zoom: 10,
        });
    }

    // Cargar el archivo
    uploadButton.addEventListener("click", () => {
        const fileInput = document.getElementById("file-input").files[0];
        if (fileInput) {
            const formData = new FormData();
            formData.append("archivo", fileInput);

            fetch("/procesar", {
                method: "POST",
                body: formData,
            })
                .then((response) => response.json())
                .then((data) => {
                    mostrarTabla(data);
                    mostrarMapa(data);
                })
                .catch((error) => console.error("Error al procesar el archivo:", error));
        }
    });

    // Mostrar la tabla editable
    function mostrarTabla(data) {
        tablaEditable.innerHTML = "";
        const table = document.createElement("table");
        const headers = ["RUTA", "PARADA", "REFERENCIA", "UBICACIÓN", "ESTATUS"];

        const headerRow = document.createElement("tr");
        headers.forEach((header) => {
            const th = document.createElement("th");
            th.textContent = header;
            headerRow.appendChild(th);
        });
        table.appendChild(headerRow);

        data.forEach((row, index) => {
            const tr = document.createElement("tr");
            headers.forEach((header) => {
                const td = document.createElement("td");
                td.textContent = row[header];
                tr.appendChild(td);
            });
            table.appendChild(tr);
        });

        tablaEditable.appendChild(table);
    }

    // Mostrar el mapa con los puntos
    function mostrarMapa(data) {
        markers.forEach((marker) => marker.setMap(null)); // Eliminar marcadores anteriores
        markers = [];

        data.forEach((row) => {
            const [lat, lng] = row["UBICACIÓN"].split(", ").map(Number);
            const marker = new google.maps.Marker({
                position: { lat, lng },
                map: mapa,
                title: row["PARADA"],
            });
            markers.push(marker);
        });
    }

    // Inicializar el mapa cuando se carga la página
    window.initMap = initMap;
});
