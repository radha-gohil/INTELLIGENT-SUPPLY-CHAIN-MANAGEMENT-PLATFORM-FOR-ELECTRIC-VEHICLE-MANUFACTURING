const API_BASE_URL =
  "http://127.0.0.1:8000";


// ============================================================
// AUTH TOKEN
// ============================================================

export function getAuthToken() {

  return localStorage.getItem(
    "ev_supply_chain_token"
  );

}


export function setAuthToken(token) {

  if (token) {

    localStorage.setItem(
      "ev_supply_chain_token",
      token
    );

  } else {

    localStorage.removeItem(
      "ev_supply_chain_token"
    );

  }

}


// ============================================================
// GENERIC REQUEST
// ============================================================

async function apiRequest(
  endpoint,
  options = {}
) {

  const token =
    getAuthToken();


  const headers = {

    "Content-Type":
      "application/json",

    ...(token
      ? {
          Authorization:
            `Bearer ${token}`
        }
      : {}),

    ...(options.headers || {})

  };


  const response =
    await fetch(
      `${API_BASE_URL}${endpoint}`,
      {
        ...options,
        headers
      }
    );


  if (!response.ok) {

    let errorMessage =
      "API request failed.";


    try {

      const errorData =
        await response.json();


      if (
        Array.isArray(
          errorData.detail
        )
      ) {

        errorMessage =
          errorData.detail
            .map(
              item =>
                item.msg
            )
            .join(", ");

      } else {

        errorMessage =
          errorData.detail ||
          errorData.message ||
          errorMessage;

      }

    }
    catch {

      // Keep default error message.

    }


    throw new Error(
      errorMessage
    );

  }


  // Some API endpoints may return 204 No Content.

  if (
    response.status === 204
  ) {

    return null;

  }


  return response.json();

}


// ============================================================
// AUTHENTICATION
// ============================================================

export async function loginUser(
  email,
  password
) {

  return apiRequest(
    "/auth/login",
    {
      method: "POST",

      body: JSON.stringify({
        email,
        password
      })
    }
  );

}


export async function getCurrentUser() {

  return apiRequest(
    "/auth/me"
  );

}


export function logoutUser() {

  setAuthToken(
    null
  );

}


// ============================================================
// SUPPLIERS
// ============================================================

export async function getSuppliers() {

  return apiRequest(
    "/suppliers"
  );

}


// ============================================================
// SUPPLIER INTELLIGENCE
// ============================================================

export async function getSupplierIntelligence(
  componentId
) {

  return apiRequest(
    `/supplier-intelligence/component/${componentId}`
  );

}


// ============================================================
// SUPPLIER METRICS
// ============================================================

export async function getSupplierMetrics(
  supplierId
) {

  return apiRequest(
    `/supplier-metrics/supplier/${supplierId}`
  );

}


// ============================================================
// ALL SUPPLIER METRICS
// ============================================================

export async function getAllSupplierMetrics() {

  return apiRequest(
    "/supplier-metrics"
  );

}


// ============================================================
// SUPPLIER PERFORMANCE
// ============================================================

export async function getSupplierPerformance(
  supplierId
) {

  return apiRequest(
    `/supplier-performance/supplier/${supplierId}`
  );

}


// ============================================================
// SUPPLIER RISK
// ============================================================

export async function getSupplierRisk(
  supplierId
) {

  return apiRequest(
    `/supplier-risk/supplier/${supplierId}`
  );

}


// ============================================================
// PROCUREMENT - SUPPLIER OPTIONS
// ============================================================

export async function getSupplierOptions(
  componentId,
  requiredQuantity
) {

  return apiRequest(
    `/procurement/component/${componentId}?required_quantity=${requiredQuantity}`
  );

}


// ============================================================
// PROCUREMENT RECOMMENDATION
// ============================================================

export async function getProcurementRecommendation(
  componentId,
  requiredQuantity
) {

  return apiRequest(
    `/procurement/recommendation/${componentId}?required_quantity=${requiredQuantity}`
  );

}


// ============================================================
// PROCUREMENT SUPPLIERS
// ============================================================

export async function getProcurementSuppliers(
  componentId,
  requiredQuantity
) {

  const data =
    await getProcurementRecommendation(
      componentId,
      requiredQuantity
    );


  return (
    data.supplier_options ||
    []
  );

}


// ============================================================
// PROCUREMENT DECISION
// ============================================================

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


// ============================================================
// INVENTORY BY COMPONENT
// ============================================================

export async function getInventoryByComponent(
  componentId
) {

  return apiRequest(
    `/inventory/component/${componentId}`
  );

}


// ============================================================
// INVENTORY BY WAREHOUSE
// ============================================================

export async function getInventoryByWarehouse(
  warehouse
) {

  return apiRequest(
    `/inventory/warehouse/${encodeURIComponent(
      warehouse
    )}`
  );

}


// ============================================================
// INVENTORY RECORD
// ============================================================

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
          Number(
            componentId
          ),

        warehouse,

        quantity:
          Number(
            quantity
          ),

        reference_id:
          referenceId ||
          null

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
          Number(
            componentId
          ),

        warehouse,

        quantity:
          Number(
            quantity
          ),

        reference_id:
          referenceId ||
          null

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
          Number(
            componentId
          ),

        warehouse,

        quantity:
          Number(
            quantity
          ),

        reference_id:
          referenceId ||
          null

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
          Number(
            componentId
          ),

        source_warehouse:
          sourceWarehouse,

        destination_warehouse:
          destinationWarehouse,

        quantity:
          Number(
            quantity
          ),

        reference_id:
          referenceId ||
          null

      })
    }
  );

}


// ============================================================
// INVENTORY TRANSACTIONS
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
// UPDATE PURCHASE ORDER TRACKING
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
          currentLocation ||
          null,

        tracking_notes:
          trackingNotes ||
          null

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


// ============================================================
// PURCHASE ORDER STATUS HISTORY
// ============================================================

export async function getPurchaseOrderHistory(
  purchaseOrderId
) {

  return apiRequest(
    `/inventory/orders/${purchaseOrderId}/history`
  );

}


// ============================================================
// GET PURCHASE ORDER SHIPMENT
// ============================================================

export async function getPurchaseOrderShipment(
  purchaseOrderId
) {

  return apiRequest(
    `/inventory/orders/${purchaseOrderId}/shipment`
  );

}


// ============================================================
// CREATE PURCHASE ORDER SHIPMENT
//
// Normally the backend automatically creates a shipment when
// the purchase order reaches DISPATCHED.
// This endpoint remains useful for testing/debugging.
// ============================================================

export async function createPurchaseOrderShipment(
  purchaseOrderId
) {

  return apiRequest(
    `/inventory/orders/${purchaseOrderId}/shipment`,
    {
      method: "POST"
    }
  );

}


// ============================================================
// SIMULATE NEXT SHIPMENT GPS LOCATION
// ============================================================

export async function simulateShipmentLocation(
  purchaseOrderId
) {

  return apiRequest(
    `/inventory/orders/${purchaseOrderId}/shipment/simulate`,
    {
      method: "POST"
    }
  );

}


// ============================================================
// GET SHIPMENT GPS TRACKING HISTORY
// ============================================================

export async function getShipmentTrackingHistory(
  purchaseOrderId
) {

  return apiRequest(
    `/inventory/orders/${purchaseOrderId}/shipment/history`
  );

}


// ============================================================
// GRAPH-RAG - ASK AI
// ============================================================

export async function askGraphRAG(
  question
) {

  return apiRequest(
    "/graph-rag/ask",
    {
      method: "POST",

      body: JSON.stringify({

        question:
          question.trim()

      })
    }
  );

}


// ============================================================
// GRAPH-RAG - GRAPH SUMMARY
// ============================================================

export async function getGraphSummary() {

  return apiRequest(
    "/graph-rag/summary"
  );

}