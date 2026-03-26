te lo voy a cambiar porque lo resumio mucho: Para Camilo — endpoints que necesita el backend para sacar el mock    
                                                                        
  Hola Cami, el frontend tiene todo listo pero corre con datos falsos
  porque el backend aún no tiene estos endpoints. Te explico qué        
  necesita cada uno para que puedas priorizarlos:           
                                                                        
  ---                                                                   
  Base URL esperada por el frontend: http://localhost:8000/api/v1
                                                                        
  ---
  1. Auth                                                               
                                                            
  POST /api/v1/auth/login                                               
  Body:  { "email": string, "password": string }            
  Response: { "access_token": string, "token_type": "bearer", "user": { 
  "id", "name", "email", "specialty", "avatar_initials" } }             
                                                                        
  GET /api/v1/auth/me                                                   
  Header: Authorization: Bearer <token>                     
  Response: el mismo objeto User
                                                                        
  POST /api/v1/auth/logout
                                                                        
  ---                                                       
  2. Pacientes
                                                                        
  GET /api/v1/patients/today
  Response: Patient[]                                                   
  → { id, name, age, gender ("M"|"F"), appointment_time, specialty,
  has_alerts, last_visit }                                              
  → last_visit vacío ("") = primera consulta
                                                                        
  POST /api/v1/patients                                     
  Body: { name, age, gender, specialty }                                
  Response: Patient (con id generado)                                   
  
  ---                                                                   
  3. Resumen clínico — el más importante                    
                                                                        
  El frontend manda el texto al /api/analyze que ya tienes, y espera que
   el resultado quede guardado y luego lo pueda leer así:               
                                                            
  GET /api/v1/patients/{id}/summary                                     
  Response:                                                             
  {
    patient_id: string,                                                 
    chips: [{ label: string, variant: "danger"|"warn"|"info"|"neutral"
  }],                                                                   
    domains: [{ id, label, status: "ok"|"warn"|"danger", description }],
    timeline: [{ id, date, text, detail, is_critical: bool }],          
    safety: [{ id, variant, title, description }],                      
    consult_history: [{ id, date, summary, files: string[], is_current: 
  bool }]                                                               
  }                                                                     
                                                                        
  El resumen_ejecutivo que ya devuelve tu analyze tiene                 
  trayectoria_clinica, intervenciones_consolidadas, estado_seguridad,
  impresion_diagnostica — esos campos se mapean directamente a timeline,
   domains, safety y chips del summary.                     

  ---
  4. Panel derecho — alertas, medicamentos y pendientes
                                                                        
  El frontend tiene un panel derecho con 3 pestañas que también
  necesitan datos reales:                                               
                                                            
  GET /api/v1/patients/{id}/alerts
  Response: [{ id, variant: "danger"|"warn"|"info", label, message }]   
                                                                        
  GET /api/v1/patients/{id}/medications                                 
  Response: [{ id, name, dose, status: "active"|"suspended",            
  status_label }]                                                       
  
  GET /api/v1/patients/{id}/pending                                     
  Response: [{ id, text, date, done: bool }]                
                                                                        
  La recomendación es que cuando el LLM procese la historia clínica en  
  /api/analyze, además del resumen_ejecutivo que ya genera, extraiga y  
  guarde también:                                                       
                                                            
  - Alertas — interacciones medicamentosas, exámenes vencidos, patrones
  de descompensación
  - Medicamentos — esquema farmacológico activo e historial de
  suspendidos                                                           
  - Pendientes — tareas clínicas que el médico debería hacer en esa
  consulta, todas con done: false por defecto                           
                                                            
  Lo ideal es una sola llamada al LLM que devuelva todo junto y lo      
  persistas por patient_id. Así los GET del panel derecho solo leen lo
  que ya está guardado, sin llamar al modelo de nuevo.                  
                                                            
  ---
  5. Appointments (menor prioridad)

  POST /api/v1/appointments
  Body: { patient_id, date "YYYY-MM-DD", time "HH:MM" }                 
  Response: { id, patient_id, date, time }
                                                                        
  ---                                                       
  Prioridad sugerida:                                                   
  1. POST /api/analyze que guarde el resultado completo en DB por
  patient_id ← ya casi lo tienes                                 
  2. GET /patients/today + GET /patients/{id}/summary                   
  3. GET /patients/{id}/alerts + medications + pending
  4. Auth                                                               
  5. Appointments                                                       
                                                                        
  Con 1, 2 y 3 ya se ve el flujo completo real sin mock.

