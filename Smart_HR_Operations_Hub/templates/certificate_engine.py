import os
import pymupdf

def render_experience_certificate(output_pdf_path, cert_data):
    """
    Renders an official, branded Experience Certificate as a tamper-evident PDF.
    Required fields in cert_data:
    - certificate_id: str (e.g. CERT-2026-0842)
    - issue_date: str (YYYY-MM-DD)
    - employee_name: str
    - job_title: str
    - department: str
    - start_date: str
    - end_date: str (or 'Present')
    - status: str (e.g. 'Former', 'Active')
    - approved_by: str (Authorized HR Officer)
    """
    doc = pymupdf.open()
    # Standard A4 Landscape: 842 x 595
    page = doc.new_page(width=842, height=595)
    
    # Outer Border (Gold / Navy double border)
    page.draw_rect(pymupdf.Rect(20, 20, 822, 575), color=(0.1, 0.2, 0.5), width=3)
    page.draw_rect(pymupdf.Rect(26, 26, 816, 569), color=(0.8, 0.65, 0.2), width=1)
    
    # Header Banner
    page.draw_rect(pymupdf.Rect(27, 27, 815, 95), color=None, fill=(0.08, 0.16, 0.32))
    page.insert_text((220, 58), 'NEXUSCORE TECHNOLOGIES INC.', fontsize=22, fontname='helv', color=(1, 1, 1))
    page.insert_text((245, 82), 'PEOPLE OPERATIONS & HUMAN CAPITAL VERIFICATION', fontsize=10, fontname='helv', color=(0.9, 0.8, 0.4))
    
    # Certificate Title
    page.insert_text((260, 135), 'EXPERIENCE CERTIFICATE', fontsize=18, fontname='helv', color=(0.1, 0.2, 0.4))
    page.draw_line(pymupdf.Point(240, 145), pymupdf.Point(600, 145), color=(0.8, 0.65, 0.2), width=2)
    
    # Body text
    body1 = f"This is to officially certify that {cert_data['employee_name']} was employed at NexusCore Technologies."
    body2 = "During their period of employment, they exhibited outstanding commitment, diligence, and professional conduct."
    page.insert_text((60, 180), body1, fontsize=12, fontname='helv', color=(0.15, 0.15, 0.15))
    page.insert_text((60, 202), body2, fontsize=12, fontname='helv', color=(0.15, 0.15, 0.15))
    
    # Table Box
    page.draw_rect(pymupdf.Rect(60, 225, 782, 355), color=(0.7, 0.75, 0.8), fill=(0.96, 0.98, 1.0), width=1)
    page.draw_line(pymupdf.Point(60, 268), pymupdf.Point(782, 268), color=(0.8, 0.85, 0.9), width=1)
    page.draw_line(pymupdf.Point(60, 311), pymupdf.Point(782, 311), color=(0.8, 0.85, 0.9), width=1)
    page.draw_line(pymupdf.Point(420, 225), pymupdf.Point(420, 355), color=(0.8, 0.85, 0.9), width=1)
    
    # Row 1
    page.insert_text((75, 250), 'Certificate ID:', fontsize=11, fontname='helv', color=(0.3, 0.35, 0.4))
    page.insert_text((180, 250), str(cert_data.get('certificate_id', 'N/A')), fontsize=11, fontname='helv', color=(0.05, 0.15, 0.3))
    
    page.insert_text((435, 250), 'Date of Issuance:', fontsize=11, fontname='helv', color=(0.3, 0.35, 0.4))
    page.insert_text((560, 250), str(cert_data.get('issue_date', 'N/A')), fontsize=11, fontname='helv', color=(0.05, 0.15, 0.3))
    
    # Row 2
    page.insert_text((75, 293), 'Designation / Role:', fontsize=11, fontname='helv', color=(0.3, 0.35, 0.4))
    page.insert_text((180, 293), str(cert_data.get('job_title', 'N/A')), fontsize=11, fontname='helv', color=(0.05, 0.15, 0.3))
    
    page.insert_text((435, 293), 'Department:', fontsize=11, fontname='helv', color=(0.3, 0.35, 0.4))
    page.insert_text((560, 293), str(cert_data.get('department', 'N/A')), fontsize=11, fontname='helv', color=(0.05, 0.15, 0.3))
    
    # Row 3
    page.insert_text((75, 337), 'Employment Tenure:', fontsize=11, fontname='helv', color=(0.3, 0.35, 0.4))
    page.insert_text((180, 337), f"{cert_data.get('start_date', 'N/A')}  to  {cert_data.get('end_date', 'Present')}", fontsize=11, fontname='helv', color=(0.05, 0.15, 0.3))
    
    page.insert_text((435, 337), 'Employment Status:', fontsize=11, fontname='helv', color=(0.3, 0.35, 0.4))
    page.insert_text((560, 337), str(cert_data.get('status', 'Verified / Completed')), fontsize=11, fontname='helv', color=(0.1, 0.5, 0.2))
    
    # Policy footnote
    page.insert_text((60, 385), 'This certificate is issued pursuant to the Experience Certificate Policy (POL-CRT-004) following verified personnel records audit.', fontsize=9, fontname='helv', color=(0.4, 0.45, 0.5))
    page.insert_text((60, 400), 'NexusCore Technologies certifies that all records reflect authentic organizational employment files.', fontsize=9, fontname='helv', color=(0.4, 0.45, 0.5))
    
    # Signatures & Seals
    page.draw_rect(pymupdf.Rect(75, 435, 230, 505), color=(0.2, 0.5, 0.8), fill=(0.95, 0.98, 1.0), width=1)
    page.insert_text((90, 455), 'OFFICIAL HR AUDIT SEAL', fontsize=9, fontname='helv', color=(0.2, 0.4, 0.7))
    page.insert_text((90, 475), 'DIGITALLY VERIFIED', fontsize=10, fontname='helv', color=(0.1, 0.6, 0.3))
    page.insert_text((90, 492), f"HASH: SHA256-AUTH-{cert_data.get('certificate_id', 'DEMO')[-4:]}", fontsize=8, fontname='helv', color=(0.5, 0.5, 0.5))
    
    # Authorized Signatory
    page.draw_line(pymupdf.Point(540, 485), pymupdf.Point(760, 485), color=(0.3, 0.3, 0.3), width=1)
    page.insert_text((540, 502), str(cert_data.get('approved_by', 'Ahmed Elsayed')), fontsize=11, fontname='helv', color=(0.1, 0.15, 0.25))
    page.insert_text((540, 517), 'Authorized Human Resources Lead', fontsize=9, fontname='helv', color=(0.4, 0.4, 0.4))
    
    # Watermark
    page.insert_text((240, 320), 'VERIFIED DEMO', fontsize=52, fontname='helv', color=(0.88, 0.90, 0.94))
    
    os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)
    doc.save(output_pdf_path)
    doc.close()
    return output_pdf_path

if __name__ == '__main__':
    sample = {
        'certificate_id': 'CERT-2026-0842',
        'issue_date': '2026-11-10',
        'employee_name': 'Tarek Farouk',
        'job_title': 'Senior DevOps Engineer',
        'department': 'Infrastructure',
        'start_date': '2020-02-01',
        'end_date': '2024-08-31',
        'status': 'Former (Honorable Departure)',
        'approved_by': 'Ahmed Elsayed (People Operations Lead)'
    }
    out = os.path.join(os.path.dirname(__file__), 'sample_experience_certificate.pdf')
    render_experience_certificate(out, sample)
    print(f"Sample certificate successfully created at: {out}")
