
# New Code Working 

# import frappe
# import json
# import requests
# from html import escape
# from frappe.utils import get_url, nowdate, now_datetime
# from frappe.desk.query_report import run
# from frappe.utils.pdf import get_pdf

# @frappe.whitelist()
# def send_ar_summary_whatsapp_simple(mobile_no=None):
#     """
#     Run the standard 'Accounts Receivable Summary' report, build a simple table PDF (landscape),
#     save it as a File and send via configured WhatsApp API.
#     """
#     try:
#         # --- recipient & report ---
#         if not mobile_no:
#             mobile_no = "917698737440"  # change as needed (include country code)

#         report_name = "Accounts Receivable Summary"

#         # --- WhatsApp settings (must exist) ---
#         ws = frappe.get_doc("Whatsapp Setting")
#         if not ws.url or not ws.api_key:
#             frappe.throw("Please configure WhatsApp URL and API Key in 'Whatsapp Setting'.")

#         # --- Run the original report logic ---
#         report = run(report_name, filters={})
#         cols = report.get("columns") or []
#         rows_raw = report.get("result") or []

#         if not rows_raw:
#             frappe.throw("Report returned no data.")

#         # --- Determine header labels and keys ---
#         if cols and isinstance(cols[0], dict):
#             headers = [c.get("label") or c.get("fieldname") or "" for c in cols]
#             keys = [c.get("fieldname") for c in cols]
#         else:
#             headers = [str(c) for c in cols]
#             keys = None

#         # --- Normalize rows ---
#         table_rows = []
#         for r in rows_raw:
#             if isinstance(r, (list, tuple)):
#                 table_rows.append([("" if v is None else v) for v in r])
#             elif isinstance(r, dict):
#                 if keys and all(keys):
#                     table_rows.append([("" if r.get(k) is None else r.get(k)) for k in keys])
#                 else:
#                     table_rows.append([("" if v is None else v) for v in r.values()])
#             else:
#                 table_rows.append([str(r)])

#         # --- Build HTML ---
#         html_parts = []
#         html_parts.append("<html><head><meta charset='utf-8'/>")
#         html_parts.append("<style>")
#         html_parts.append("body{font-family: Arial, Helvetica, sans-serif; font-size:10pt}")
#         html_parts.append("table{border-collapse:collapse; width:100%}")
#         html_parts.append("th,td{border:1px solid #ddd; padding:6px; text-align:left; vertical-align:top}")
#         html_parts.append("th{background:#f2f2f2; font-weight:600}")
#         html_parts.append(".title{text-align:center; font-size:14pt; margin-bottom:10px}")
#         html_parts.append("</style></head><body>")
#         html_parts.append(f"<div class='title'>{escape(report_name)} - {nowdate()}</div>")
#         html_parts.append("<table><thead><tr>")

#         for h in headers:
#             html_parts.append(f"<th>{escape(str(h))}</th>")
#         html_parts.append("</tr></thead><tbody>")

#         for r in table_rows:
#             html_parts.append("<tr>")
#             for cell in r:
#                 cell_text = "" if cell is None else str(cell)
#                 html_parts.append(f"<td>{escape(cell_text)}</td>")
#             html_parts.append("</tr>")

#         html_parts.append("</tbody></table>")
#         html_parts.append("</body></html>")

#         html = "".join(html_parts)

#         # --- PDF in Landscape ---
#         pdf_bytes = get_pdf(html, options={"orientation": "Landscape"})

#         # --- Save File ---
#         file_name = f"AR_Summary_{nowdate()}.pdf"
#         file_doc = frappe.get_doc({
#             "doctype": "File",
#             "file_name": file_name,
#             "attached_to_doctype": "Report",
#             "attached_to_name": report_name,
#             "is_private": 0,
#             "content": pdf_bytes
#         })
#         file_doc.save(ignore_permissions=True)
#         frappe.db.commit()
#         file_url = get_url() + file_doc.file_url

#         # --- WhatsApp Payload ---
#         payload = {
#             "apiKey": ws.api_key,
#             "campaignName": "monthly_ledger_new",
#             "destination": mobile_no,
#             "userName": "Finance Team",
#             "source": report_name,
#             "media": {
#                 "url": file_url,
#                 "filename": file_name
#             },
#             "templateParams": [],
#             "tags": [report_name]
#         }

#         resp = requests.post(
#             ws.url,
#             data=json.dumps(payload),
#             headers={"Content-Type": "application/json"},
#             timeout=15
#         )

#         status = "Sent" if resp.status_code == 200 else f"Failed ({resp.status_code})"

#         # --- Log status ---
#         try:
#             frappe.get_doc({
#                 "doctype": "Whatsapp Log",
#                 "document_name": report_name,
#                 "mobile_no": mobile_no,
#                 "url": file_url,
#                 "status": status,
#                 "response": resp.text,
#                 "sent_on": now_datetime()
#             }).insert(ignore_permissions=True)
#             frappe.db.commit()
#         except Exception:
#             frappe.log_error(frappe.get_traceback(), "Failed to insert Whatsapp Log")

#         return {"status": status, "http_code": resp.status_code, "response": resp.text, "file_url": file_url}

#     except Exception:
#         frappe.log_error(frappe.get_traceback(), "Error sending AR Summary via WhatsApp")
#         return {"status": "Failed", "message": frappe.get_traceback()}


##New Code \

import frappe
import json
import requests
from html import escape
from frappe.utils import get_url, nowdate, now_datetime
from frappe.desk.query_report import run
from frappe.utils.pdf import get_pdf

@frappe.whitelist()
def send_ar_summary_whatsapp_simple(mobile_no=None):
    """
    Run the standard 'Accounts Receivable Summary' report, build a simple table PDF (landscape),
    save it as a File and send via configured WhatsApp API.
    """
    try:
        # --- recipient & report ---
        if not mobile_no:
            mobile_no = "917698737440"  # fallback number (include country code)

        report_name = "Accounts Receivable Summary"

        # --- WhatsApp settings (must exist) ---
        ws = frappe.get_doc("Whatsapp Setting")
        if not ws.url or not ws.api_key:
            frappe.throw("Please configure WhatsApp URL and API Key in 'Whatsapp Setting'.")

        # --- Run the report ---
        report = run(report_name, filters={})
        cols = report.get("columns") or []
        rows_raw = report.get("result") or []

        if not rows_raw:
            frappe.throw("Report returned no data.")

        # --- Build headers & keys ---
        if cols and isinstance(cols[0], dict):
            headers = [c.get("label") or c.get("fieldname") or "" for c in cols]
            keys = [c.get("fieldname") for c in cols]
        else:
            headers = [str(c) for c in cols]
            keys = None

        # --- Normalize rows ---
        table_rows = []
        for r in rows_raw:
            if isinstance(r, (list, tuple)):
                table_rows.append([("" if v is None else v) for v in r])
            elif isinstance(r, dict):
                if keys and all(keys):
                    table_rows.append([("" if r.get(k) is None else r.get(k)) for k in keys])
                else:
                    table_rows.append([("" if v is None else v) for v in r.values()])
            else:
                table_rows.append([str(r)])

        # --- Build HTML ---
        html_parts = []
        html_parts.append("<html><head><meta charset='utf-8'/>")
        html_parts.append("<style>")
        html_parts.append("body{font-family: Arial, Helvetica, sans-serif; font-size:10pt}")
        html_parts.append("table{border-collapse:collapse; width:100%}")
        html_parts.append("th,td{border:1px solid #ddd; padding:6px; text-align:left; vertical-align:top}")
        html_parts.append("th{background:#f2f2f2; font-weight:600}")
        html_parts.append(".title{text-align:center; font-size:14pt; margin-bottom:10px}")
        html_parts.append("</style></head><body>")
        html_parts.append(f"<div class='title'>{escape(report_name)} - {nowdate()}</div>")
        html_parts.append("<table><thead><tr>")

        for h in headers:
            html_parts.append(f"<th>{escape(str(h))}</th>")
        html_parts.append("</tr></thead><tbody>")

        for r in table_rows:
            html_parts.append("<tr>")
            for cell in r:
                cell_text = "" if cell is None else str(cell)
                html_parts.append(f"<td>{escape(cell_text)}</td>")
            html_parts.append("</tr>")

        html_parts.append("</tbody></table>")
        html_parts.append("</body></html>")
        html = "".join(html_parts)

        # --- PDF in Landscape ---
        pdf_bytes = get_pdf(html, options={"orientation": "Landscape"})

        # --- Save File ---
        file_name = f"AR_Summary_{nowdate()}.pdf"
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": file_name,
            "attached_to_doctype": "Report",
            "attached_to_name": report_name,
            "is_private": 0,
            "content": pdf_bytes
        })
        file_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        file_url = get_url() + file_doc.file_url

        frappe.logger().info(f"✅ File created: {file_doc.name}, URL: {file_url}")

        # --- WhatsApp Payload ---
        payload = {
            "apiKey": ws.api_key,
            "campaignName": "monthly_ledger_new",
            "destination": mobile_no,
            "userName": "Finance Team",
            "source": report_name,
            "media": {
                "url": file_url,
                "filename": file_name
            },
            "templateParams": [],
            "tags": [report_name]
        }

        try:
            resp = requests.post(
                ws.url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            frappe.logger().info(f"📩 WhatsApp API response: {resp.status_code} - {resp.text}")
        except Exception as e:
            frappe.log_error(f"WhatsApp API Error: {str(e)}", "AR Summary WhatsApp")
            return {"status": "Failed", "message": str(e)}

        status = "Sent" if resp.status_code == 200 else f"Failed ({resp.status_code})"

        # --- Log status ---
        try:
            frappe.get_doc({
                "doctype": "Whatsapp Log",
                "document_name": report_name,
                "mobile_no": mobile_no,
                "url": file_url,
                "status": status,
                "response": resp.text,
                "sent_on": now_datetime()
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Failed to insert Whatsapp Log")

        return {
            "status": status,
            "http_code": resp.status_code,
            "response": resp.text,
            "file_url": file_url
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Error sending AR Summary via WhatsApp")
        return {"status": "Failed", "message": frappe.get_traceback()}
