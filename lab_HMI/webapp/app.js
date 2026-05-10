const TASK = "T_ROB1";
const MODULE = "HMIData";

var startBtn, decBtn, incBtn, switchDO1;
var rapidColor, rapidStart, rapidBusy, rapidCount, rapidQty;
var selectedColor = 0;
var qty = 1;

window.addEventListener("load", async function () {
    fpComponentsEnableLog();
    createHMI();
});

async function createHMI() {
    try {
        // 0. Botones de color
        document.getElementById("btn-green").addEventListener("click", () => selectColor(4));
        document.getElementById("btn-blue").addEventListener("click",  () => selectColor(2));
        document.getElementById("btn-red").addEventListener("click",   () => selectColor(3));

        // 1. Botones +/- para la Meta
        decBtn = new FPComponents.Button_A();
        decBtn.text = "−";
        decBtn.onclick = async () => {
            qty = Math.max(1, qty - 1);
            document.getElementById("qty-label").textContent = qty;
            if (rapidQty) await rapidQty.setValue(qty);
        };
        decBtn.attachToId("btn-dec");

        incBtn = new FPComponents.Button_A();
        incBtn.text = "+";
        incBtn.onclick = async () => {
            qty = Math.min(99, qty + 1);
            document.getElementById("qty-label").textContent = qty;
            if (rapidQty) await rapidQty.setValue(qty);
        };
        incBtn.attachToId("btn-inc");

        // 2. Botón Iniciar
        startBtn = new FPComponents.Button_A();
        startBtn.text = "▶ INICIAR RECOGIDA";
        startBtn.highlight = true;
        startBtn.attachToId("btn-start");
        const COLOR_NAMES = { 1: "Amarillo", 2: "Azul", 3: "Rojo", 4: "Verde" };
        startBtn.onclick = async () => {
            if (selectedColor === 0) {
                FPComponents.Popup_A.message("Aviso", "Selecciona un color primero.");
                return;
            }
            if (!rapidStart) {
                FPComponents.Popup_A.message("Sin conexión RAPID", "Comprueba que HMIData.mod está cargado y el programa está corriendo.");
                return;
            }
            FPComponents.Popup_A.confirm(
                "Confirmar inicio",
                "¿Iniciar recogida de pieza " + COLOR_NAMES[selectedColor] + "?",
                async function (action) {
                    if (action === FPComponents.Popup_A.OK) {
                        await rapidStart.setValue(true).catch(e => FPComponents.Popup_A.message("Error", String(e)));
                    }
                }
            );
        };

        // 3. Switch DO1 (imán — lectura y escritura)
        try {
            switchDO1 = new FPComponents.Switch_A();
            switchDO1.desc = "DO1 – Imán";
            switchDO1.attachToId("switchDO1");
            switchDO1.onchange = async function () {
                try {
                    const sig = await RWS.IO.getSignal("Local_IO_0_DO1");
                    const val = await sig.getValue();
                    await RWS.IO.setSignalValue("Local_IO_0_DO1", val == 1 ? 0 : 1);
                } catch (e) { console.error("Error switch DO1:", e); }
            };
            const sig = await RWS.IO.getSignal("Local_IO_0_DO1");
            sig.addCallbackOnChanged(v => { switchDO1.active = (v == 1); });
            sig.subscribe(true);
        } catch (e) { console.warn("DO1 no disponible:", e); }

        // 4. Suscripción a RAPID — cada variable en su propio try/catch
        try { rapidColor = await RWS.Rapid.getData(TASK, MODULE, "selectedColor"); }
        catch (e) { console.warn("rapidColor:", e); }

        try { rapidQty = await RWS.Rapid.getData(TASK, MODULE, "piecesToPick"); }
        catch (e) { console.warn("rapidQty:", e); }

        try { rapidStart = await RWS.Rapid.getData(TASK, MODULE, "startPick"); }
        catch (e) {
            console.warn("rapidStart:", e);
            document.getElementById("status-indicator").textContent = "SIN RAPID";
        }

        try {
            rapidBusy = await RWS.Rapid.getData(TASK, MODULE, "robotBusy");
            rapidBusy.addCallbackOnChanged(v => {
                const el = document.getElementById("status-indicator");
                const busy = (v === true || v === "TRUE");
                el.textContent = busy ? "OCUPADO" : "LIBRE";
                el.className = busy ? "status-busy" : "status-idle";
            });
            await rapidBusy.subscribe(true);
        } catch (e) { console.warn("rapidBusy:", e); }

        try {
            rapidCount = await RWS.Rapid.getData(TASK, MODULE, "piecesPickedCount");
            rapidCount.addCallbackOnChanged(v => {
                document.getElementById("piece-count").textContent = v;
            });
            await rapidCount.subscribe(true);
        } catch (e) { console.warn("rapidCount:", e); }

    } catch (e) { console.error("Error inicializando HMI:", e); }
}

function selectColor(id) {
    selectedColor = id;
    document.querySelectorAll(".color-btn").forEach(b => b.classList.remove("selected"));
    const colors = { 1: "btn-yellow", 2: "btn-blue", 3: "btn-red", 4: "btn-green" };
    document.getElementById(colors[id]).classList.add("selected");
    if (rapidColor) rapidColor.setValue(id).catch(() => {});
}