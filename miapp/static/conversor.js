//  PASO CRÍTICO: REEMPLAZA "TU_CLAVE_AQUI" con tu API Key real de ExchangeRate-API
const API_KEY = "93371013f9-b72754b2b0-t4tell"; 
const API_BASE_URL = `https://v6.exchangerate-api.com/v6/${API_KEY}/latest/`;



function getMoneda(pais) {
    switch (pais) {
        case 'Chile': return 'CLP';
        case 'Colombia': return 'COP';
        case 'Perú': return 'PEN';
        default: return '';
    }
}

// Función adaptada para usar los factores fijos de tu mantenedor, 
// pero multiplicados por el monto convertido (como en tu lógica original)
function getFactorFijo(pais) {
    switch (pais) {
        // Factores de tu código original: 
        case 'Chile': return 0.000034; 
        case 'Colombia': return 0.000025; 
        case 'Perú': return 0.000030; 
        default: return 0;
    }
}

function getFactorTributario(pais, montoConvertido) {
    // Factor es igual al monto convertido multiplicado por la tasa fija.
    const factorFijo = getFactorFijo(pais);
    return montoConvertido * factorFijo;
}

function formatCurrency(amount, currency) {
    // Formatea el número a moneda con dos decimales, usando el estándar chileno como base.
    return new Intl.NumberFormat('es-CL', { style: 'currency', currency: currency, minimumFractionDigits: 2 }).format(amount);
}

// ------------------
// INTEGRACIÓN ASÍNCRONA CON LA API
// ------------------

async function getExchangeRate(source, target) {
    if (source === target) return 1;

    try {

        const url = `${API_BASE_URL}${source}`;
        
        const response = await fetch(url);
        

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}. Revisa tu API Key.`);
        }
        
        const data = await response.json();


        if (data.result === "success" && data.conversion_rates[target]) {
            return data.conversion_rates[target];
        } else {
            console.error("Respuesta de la API fallida:", data);
            alert("Error de la API. Verifica tu clave o la moneda de origen.");
            return 0; 
        }
    } catch (error) {
        console.error("Error al conectar con la API:", error);
        alert("Error de conexión. Asegúrate de estar conectado a internet y que tu clave sea válida.");
        return 0; // Devuelve 0 en caso de fallo total
    }
}

// ------------------
// FUNCIÓN PRINCIPAL DE CONVERSIÓN
// ------------------

async function convertAndCalculate() {
    const amount = parseFloat(document.getElementById('input-amount').value);
    const sourceCurrency = document.getElementById('select-source').value;
    const targetCountry = document.getElementById('select-country').value;
    
    if (isNaN(amount) || amount <= 0) {
        alert('Por favor, ingresa un monto válido.');
        return;
    }

    const targetCurrency = getMoneda(targetCountry);
    
    // 1. OBTENER TASA (Llama a la API y espera la respuesta)
    document.getElementById('result-container').innerHTML = '<div>Cargando tasa de cambio...</div>';
    const rate = await getExchangeRate(sourceCurrency, targetCurrency);
    
    if (rate === 0) {
        document.getElementById('result-container').innerHTML = '<div>No se pudo completar la conversión debido a un error en la tasa.</div>';
        return; 
    }

    // 2. CONVERSIÓN PURA
    const convertedAmount = amount * rate;
    
    // 3. CÁLCULO DEL FACTOR TRIBUTARIO (TU LÓGICA)
    const factorTributario = getFactorTributario(targetCountry, convertedAmount);
    
    // 4. MONTO TOTAL
    const totalAmount = convertedAmount + factorTributario;

    // 5. MOSTRAR RESULTADOS
    const resultsHTML = `
        <div>Monto Inicial (${sourceCurrency}): <strong>${formatCurrency(amount, sourceCurrency)}</strong></div>
        <div>Tasa de Conversión (Obtenida por API): <strong>${rate.toFixed(4)}</strong></div>
        <hr>
        <div>Monto Convertido (Puro): <strong>${formatCurrency(convertedAmount, targetCurrency)}</strong></div>
        <div>Factor Tributario Simulado (${targetCountry}): <strong>+ ${formatCurrency(factorTributario, targetCurrency)}</strong></div>
        <hr>
        <div class="result-total">Monto Total con Factor Tributario: <strong>${formatCurrency(totalAmount, targetCurrency)}</strong></div>
        <div class="small" style="margin-top: 10px;">* El factor tributario es una simulación basada en la lógica de tu mantenedor.</div>
    `;
    
    document.getElementById('result-container').innerHTML = resultsHTML;
}
