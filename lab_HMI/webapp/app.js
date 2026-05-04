// Pick & Place HMI — basado en GOFA-webapp del profesor (edwinDOS)

const TASK   = "T_ROB1";
const MODULE = "HMIData";

const COLOR_NAMES = { 0: "—", 1: "Amarillo", 2: "Azul", 3: "Rojo" };
const COLOR_IDS   = ["", "btn-yellow", "btn-blue", "btn-red"];

var selectedColor = 0;
var qty = 1;

var startBtn, incBtn, decBtn;
var rapidColor, rapidStart, rapidBusy, rapidCount, rapidQty;
var switchDO1, switchDO2, ledMagnet;

window.addEventListener("load", async function () {
    fpComponentsEnableLog();
    createMainContent();
});

function createMainContent() {
    Create_QtyButtons();
    Create_StartButton();
    Create_SwitchDO1();
    Create_SwitchDO2();
    Create_LedMagnet();
    Subscribe_RapidVars();
}

// ─── SELECCIÓN DE COLOR (llamada desde los botones HTML) ──────────────────────
function selectColor(colorId) {
    selectedColor = colorId;
    document.querySelectorAll(".color-btn").forEach(b => b.classList.remove("selected"));
    document.getElementById(COLOR_IDS[colorId]).classList.add("selected");
    if (rapidColor) rapidColor.setValue(colorId).catch(handleError);
}

// ─── BOTONES +/- CANTIDAD ─────────────────────────────────────────────────────
function Create_QtyButtons() {
    try {
        decBtn = new FPComponents.Button_A();
        decBtn.attachToId("btn-dec");
        decBtn.text = "−";
        decBtn.onclick = async () => {
            qty = Math.max(1, qty - 1);
            document.getElementById("qty-label").textContent = qty;
            if (rapidQty) await rapidQty.setValue(qty).catch(handleError);
        };

        incBtn = new FPComponents.Button_A();
        incBtn.attachToId("btn-inc");
        incBtn.text = "+";
        incBtn.onclick = async () => {
            qty = Math.min(99, qty + 1);
            document.getElementById("qty-label").textContent = qty;
            if (rapidQty) await rapidQty.setValue(qty).catch(handleError);
        };
    } catch (e) { console.log("Error en botones cantidad: " + e); }
}

// ─── BOTÓN INICIAR ────────────────────────────────────────────────────────────
function Create_StartButton() {
    try {
        startBtn = new FPComponents.Button_A();
        startBtn.attachToId("btn-start");
        startBtn.text = "▶  INICIAR RECOGIDA";
        startBtn.onclick = async () => {
            if (selectedColor === 0) {
                FPComponents.Popup_A.message("Sin pieza seleccionada", "Elige un color antes de iniciar.");
                return;
            }
            FPComponents.Popup_A.confirm(
                "Confirmar inicio",
                "¿Iniciar recogida de pieza " + COLOR_NAMES[selectedColor] + "?",
                async function (action) {
                    if (action === FPComponents.Popup_A.OK) {
                        try {
                            await rapidStart.setValue(true);
                        } catch (e) { handleError(e); }
                    }
                }
            );
        };
    } catch (e) { console.log("Error en botón inicio: " + e); }
}

// ─── SWITCH DO1 (imán) ────────────────────────────────────────────────────────
function Create_SwitchDO1() {
    try {
        switchDO1 = new FPComponents.Switch_A();
        switchDO1.desc = "DO1 Imán";
        switchDO1.attachToId("switchDO1");
        switchDO1.onchange = async function () {
            var sig = await RWS.IO.getSignal("Local_IO_0_DO1");
            var val = await sig.getValue();
            await RWS.IO.setSignalValue("Local_IO_0_DO1", val == 1 ? 0 : 1);
        };
    } catch (e) { console.log("Error en switch DO1: " + e); }
}

// ─── SWITCH DO2 ───────────────────────────────────────────────────────────────
function Create_SwitchDO2() {
    try {
        switchDO2 = new FPComponents.Switch_A();
        switchDO2.desc = "DO2";
        switchDO2.attachToId("switchDO2");
        switchDO2.onchange = async function () {
            var sig = await RWS.IO.getSignal("Local_IO_0_DO2");
            var val = await sig.getValue();
            await RWS.IO.setSignalValue("Local_IO_0_DO2", val == 1 ? 0 : 1);
        };
    } catch (e) { console.log("Error en switch DO2: " + e); }
}

// ─── LED INDICADOR IMÁN (DO1) ─────────────────────────────────────────────────
function Create_LedMagnet() {
    try {
        ledMagnet = new FPComponents.Digital_A();
        ledMagnet.desc = "DO1";
        ledMagnet.attachToId("led-magnet");
        ledMagnet.onclick = null; // solo lectura
        RWS.IO.getSignal("Local_IO_0_DO1").then(sig => {
            sig.addCallbackOnChanged(val => {
                if (val === undefined) sig.getValue().then(v => { ledMagnet.active = (v == 1); });
                else ledMagnet.active = (val == 1);
            });
            sig.subscribe(true);
        }).catch(handleError);
    } catch (e) { console.log("Error en LED magneto: " + e); }
}

// ─── SUSCRIPCIÓN A VARIABLES RAPID ───────────────────────────────────────────
async function Subscribe_RapidVars() {
    try {
        rapidColor = await RWS.Rapid.getData(TASK, MODULE, "selectedColor");
        await rapidColor.subscribe(true);

        rapidStart = await RWS.Rapid.getData(TASK, MODULE, "startPick");
        await rapidStart.subscribe(true);

        rapidQty = await RWS.Rapid.getData(TASK, MODULE, "piecesToPick");
        await rapidQty.subscribe(true);

        rapidBusy = await RWS.Rapid.getData(TASK, MODULE, "robotBusy");
        rapidBusy.addCallbackOnChanged(async (val) => {
            var v = val === undefined ? await rapidBusy.getValue() : val;
            var busy = (v === true || v === "TRUE");
            var el = document.getElementById("status-indicator");
            el.textContent = busy ? "OCUPADO" : "LIBRE";
            el.className   = busy ? "status-busy" : "status-idle";
            if (startBtn) startBtn.enabled = !busy;
        });
        await rapidBusy.subscribe(true);

        rapidCount = await RWS.Rapid.getData(TASK, MODULE, "piecesPickedCount");
        rapidCount.addCallbackOnChanged(async (val) => {
            var v = val === undefined ? await rapidCount.getValue() : val;
            document.getElementById("piece-count").textContent = v;
        });
        await rapidCount.subscribe(true);

        selectColor(1); // amarillo seleccionado por defecto al arrancar

    } catch (e) {
        FPComponents.Popup_A.message(
            "Error conectando con RAPID",
            "Comprueba que HMIData.mod está cargado.\n" + String(e.message || e)
        );
    }
}

function handleError(e) {
    FPComponents.Popup_A.message("Error", String(e.message || e));
}

// ─── CICLO DE VIDA (requerido por SDK) ───────────────────────────────────────
var appActivate = async function () {
    if (rapidBusy)  await rapidBusy.subscribe(true);
    if (rapidCount) await rapidCount.subscribe(true);
    if (rapidColor) await rapidColor.subscribe(true);
    if (rapidStart) await rapidStart.subscribe(true);
    if (rapidQty)   await rapidQty.subscribe(true);
    return true;
};

var appDeactivate = async function () {
    if (rapidBusy)  await rapidBusy.unsubscribe();
    if (rapidCount) await rapidCount.unsubscribe();
    if (rapidColor) await rapidColor.unsubscribe();
    if (rapidStart) await rapidStart.unsubscribe();
    if (rapidQty)   await rapidQty.unsubscribe();
    return true;
};
