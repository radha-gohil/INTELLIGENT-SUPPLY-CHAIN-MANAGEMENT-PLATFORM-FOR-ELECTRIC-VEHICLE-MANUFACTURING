const API_BASE_URL = "http://127.0.0.1:8000";


// ============================================================
// GENERIC REQUEST
// ============================================================

async function apiRequest(
  endpoint,
  options = {}
) {

  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {})
      },
      ...options
    }
  );


  if (!response.ok) {

    let errorMessage =
      "API request failed.";

    try {

      const errorData =
        await response.json();

      errorMessage =
        errorData.detail ||
        errorMessage;

    }

    catch {

      // Keep default error.

    }


    throw new Error(
      errorMessage
    );

  }


  return response.json();

}


// ============================================================
// SUPPLIERS
// ============================================================

export async function getSuppliers() {

  return apiRequest(
    "/suppliers"
  );

}


export async function getSupplierIntelligence(
  componentId
) {

  return apiRequest(
    `/supplier-intelligence/component/${componentId}`
  );

}


export async function getSupplierMetrics(
  supplierId
) {

  return apiRequest(
    `/supplier-metrics/supplier/${supplierId}`
  );

}


export async function getAllSupplierMetrics() {

  return apiRequest(
    "/supplier-metrics"
  );

}


export async function getSupplierPerformance(
  supplierId
) {

  return apiRequest(
    `/supplier-performance/supplier/${supplierId}`
  );

}


export async function getSupplierRisk(
  supplierId
) {

  return apiRequest(
    `/supplier-risk/supplier/${supplierId}`
  );

}


// ============================================================
// PROCUREMENT
// ============================================================

export async function getSupplierOptions(
  componentId,
  requiredQuantity
) {

  return apiRequest(
    `/procurement/component/${componentId}?required_quantity=${requiredQuantity}`
  );

}


export async function getProcurementRecommendation(
  componentId,
  requiredQuantity
) {

  return apiRequest(
    `/procurement/recommendation/${componentId}?required_quantity=${requiredQuantity}`
  );

}


export async function getProcurementSuppliers(
  componentId,
  requiredQuantity
) {

  const data =
    await getProcurementRecommendation(
      componentId,
      requiredQuantity
    );


  return data.supplier_options || [];

}


export async function getProcurementDecision(
  componentId,
  requiredQuantity
) {

  return getProcurementRecommendation(
    componentId,
    requiredQuantity
  );

}


// ============================================================
// INVENTORY VEHICLES
// ============================================================

export async function getInventoryVehicles() {

  return apiRequest(
    "/inventory/vehicles"
  );

}


// ============================================================
// VEHICLE BOM + CURRENT INVENTORY
// ============================================================

export async function getVehicleInventoryComponents(
  vehicleId
) {

  return apiRequest(
    `/inventory/vehicle/${vehicleId}/components`
  );

}


// ============================================================
// VEHICLE REQUIREMENT ANALYSIS
// ============================================================

export async function getVehicleRequirementAnalysis(
  vehicleId,
  plannedQuantity,
  requiredDate
) {

  const query =
    new URLSearchParams({

      planned_quantity:
        String(
          plannedQuantity
        ),

      required_date:
        requiredDate

    });


  return apiRequest(

    `/inventory/vehicle/${vehicleId}/requirements?${query.toString()}`

  );

}


// ============================================================
// INVENTORY
// ============================================================

export async function getInventory() {

  return apiRequest(
    "/inventory"
  );

}


export async function getInventoryByComponent(
  componentId
) {

  return apiRequest(
    `/inventory/component/${componentId}`
  );

}


export async function getInventoryByWarehouse(
  warehouse
) {

  return apiRequest(
    `/inventory/warehouse/${encodeURIComponent(warehouse)}`
  );

}


export async function getInventoryRecord(
  inventoryId
) {

  return apiRequest(
    `/inventory/${inventoryId}`
  );

}


// ============================================================
// RECEIVE STOCK
// ============================================================

export async function receiveStock(
  componentId,
  warehouse,
  quantity,
  referenceId = null
) {

  return apiRequest(
    "/inventory/receipt",
    {
      method: "POST",

      body: JSON.stringify({

        component_id:
          Number(componentId),

        warehouse,

        quantity:
          Number(quantity),

        reference_id:
          referenceId || null

      })
    }
  );

}


// ============================================================
// ISSUE STOCK
// ============================================================

export async function issueStock(
  componentId,
  warehouse,
  quantity,
  referenceId = null
) {

  return apiRequest(
    "/inventory/issue",
    {
      method: "POST",

      body: JSON.stringify({

        component_id:
          Number(componentId),

        warehouse,

        quantity:
          Number(quantity),

        reference_id:
          referenceId || null

      })
    }
  );

}


// ============================================================
// ADJUST STOCK
// ============================================================

export async function adjustStock(
  componentId,
  warehouse,
  quantity,
  referenceId = null
) {

  return apiRequest(
    "/inventory/adjustment",
    {
      method: "POST",

      body: JSON.stringify({

        component_id:
          Number(componentId),

        warehouse,

        quantity:
          Number(quantity),

        reference_id:
          referenceId || null

      })
    }
  );

}


// ============================================================
// TRANSFER STOCK
// ============================================================

export async function transferStock(
  componentId,
  sourceWarehouse,
  destinationWarehouse,
  quantity,
  referenceId = null
) {

  return apiRequest(
    "/inventory/transfer",
    {
      method: "POST",

      body: JSON.stringify({

        component_id:
          Number(componentId),

        source_warehouse:
          sourceWarehouse,

        destination_warehouse:
          destinationWarehouse,

        quantity:
          Number(quantity),

        reference_id:
          referenceId || null

      })
    }
  );

}


// ============================================================
// TRANSACTIONS
// ============================================================

export async function getInventoryTransactions() {

  return apiRequest(
    "/inventory/transactions/all"
  );

}
// ============================================================
// PURCHASE ORDER TRACKING
// ============================================================

export async function getPurchaseOrders(
  includeHistorical = false
) {

  return apiRequest(
    `/inventory/orders?include_historical=${includeHistorical}`
  );

}


// ============================================================
// CREATE PURCHASE ORDER
// ============================================================

export async function createPurchaseOrder(
  order
) {

  return apiRequest(
    "/inventory/orders",
    {
      method: "POST",

      body: JSON.stringify(
        order
      )
    }
  );

}


// ============================================================
// GET PURCHASE ORDER
// ============================================================

export async function getPurchaseOrder(
  purchaseOrderId
) {

  return apiRequest(
    `/inventory/orders/${purchaseOrderId}`
  );

}


// ============================================================
// UPDATE TRACKING
// ============================================================

export async function updatePurchaseOrderTracking(
  purchaseOrderId,
  trackingStage,
  currentLocation = null,
  trackingNotes = null
) {

  return apiRequest(
    `/inventory/orders/${purchaseOrderId}/tracking`,
    {
      method: "PATCH",

      body: JSON.stringify({

        tracking_stage:
          trackingStage,

        current_location:
          currentLocation || null,

        tracking_notes:
          trackingNotes || null

      })
    }
  );

}


// ============================================================
// RECEIVE PURCHASE ORDER
// ============================================================

export async function receivePurchaseOrder(
  purchaseOrderId,
  quantityReceived
) {

  return apiRequest(
    `/inventory/orders/${purchaseOrderId}/receive`,
    {
      method: "POST",

      body: JSON.stringify({

        quantity_received:
          Number(
            quantityReceived
          )

      })
    }
  );

}