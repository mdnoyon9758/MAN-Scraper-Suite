#!/usr/bin/env python3
"""
Enhanced Data Exporter
Handles exporting data to various file formats with professional styling
"""

import pandas as pd
from pandas import DataFrame
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import csv
import openpyxl
from datetime import datetime
import os

class DataExporter:
    """
    Professional Data Exporter with structured design and styling
    Supports CSV, JSON, Excel, and PDF with enhanced formatting
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # Default output directory to W: if not specified
        output_dir = config.get('export', {}).get('output_dir', 'W:\\')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _prepare_metadata(self, data: List[Dict[str, Any]], topic: str = "") -> Dict[str, Any]:
        """Prepare metadata for exports"""
        return {
            'export_timestamp': datetime.now().isoformat(),
            'total_records': len(data),
            'topic_searched': topic,
            'data_source': 'MAN Scraper Suite',
            'columns': list(data[0].keys()) if data else [],
        }

    def export_to_csv(self, data: List[Dict[str, Any]], filename: str, topic: str = "") -> Path:
        """Export data to professionally formatted CSV"""
        filepath = self.output_dir / f"{filename}.csv"
        
        if not data:
            print("No data to export to CSV")
            return filepath
            
        # Create DataFrame with proper column names
        df = DataFrame(data)
        
        # Rename columns to be more user-friendly
        column_mapping = {
            'url': 'Source_URL',
            'title': 'Title',
            'text': 'Content', 
            'platform': 'Platform',
            'timestamp': 'Date_Time',
            'author': 'Author',
            'engagement': 'Engagement_Score'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df.rename(columns={old_col: new_col}, inplace=True)
        
        # Add metadata row at the top
        metadata = self._prepare_metadata(data, topic)
        metadata_row = {col: '' for col in df.columns}
        metadata_row[df.columns[0]] = f"Topic: {topic}" if topic else "Data Export"
        metadata_row[df.columns[1] if len(df.columns) > 1 else df.columns[0]] = f"Exported: {metadata['export_timestamp']}"
        
        # Insert metadata at the beginning
        df_with_meta = DataFrame([metadata_row] + df.to_dict('records'))
        
        # Export to CSV
        df_with_meta.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        print(f"✅ CSV Exported: {filepath} ({len(data)} records)")
        return filepath

    def export_to_json(self, data: List[Dict[str, Any]], filename: str, topic: str = "") -> Path:
        """Export data to structured JSON with metadata"""
        filepath = self.output_dir / f"{filename}.json"
        
        metadata = self._prepare_metadata(data, topic)
        
        structured_export = {
            'metadata': metadata,
            'summary': {
                'total_records': len(data),
                'platforms_covered': len(set(item.get('platform', 'unknown') for item in data)),
                'date_range': {
                    'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'topic': topic
                }
            },
            'data': data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(structured_export, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ JSON Exported: {filepath} ({len(data)} records)")
        return filepath

    def export_to_excel(self, data: List[Dict[str, Any]], filename: str, topic: str = "") -> Path:
        """Export data to professionally styled Excel"""
        filepath = self.output_dir / f"{filename}.xlsx"
        
        if not data:
            print("No data to export to Excel")
            return filepath
            
        df = DataFrame(data)
        
        # Create Excel writer with xlsxwriter engine for styling
        try:
            import xlsxwriter
            writer = DataFrame.ExcelWriter(filepath, engine='xlsxwriter')
            
            # Write data to Excel
            df.to_excel(writer, sheet_name='Data', index=False)
            
            # Get workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Data']
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#4472C4',
                'font_color': 'white',
                'border': 1
            })
            
            cell_format = workbook.add_format({
                'text_wrap': True,
                'valign': 'top',
                'border': 1
            })
            
            # Apply header format
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 20)  # Set column width
            
            # Apply alternating row colors
            for row_num in range(1, len(df) + 1):
                for col_num in range(len(df.columns)):
                    if row_num % 2 == 0:
                        bg_format = workbook.add_format({'fg_color': '#F2F2F2', 'border': 1})
                    else:
                        bg_format = cell_format
                    worksheet.write(row_num, col_num, df.iloc[row_num-1, col_num], bg_format)
            
            # Add metadata sheet
            metadata = self._prepare_metadata(data, topic)
            metadata_df = DataFrame(list(metadata.items()), columns=['Field', 'Value'])
            metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            writer.close()
            
        except ImportError:
            # Fallback to basic Excel export
            df.to_excel(filepath, index=False)
        
        print(f"✅ Excel Exported: {filepath} ({len(data)} records)")
        return filepath

    def export_to_pdf(self, data: List[Dict[str, Any]], filename: str, topic: str = "") -> Path:
        """Export data to professionally formatted PDF"""
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        filepath = self.output_dir / f"{filename}.pdf"
        
        if not data:
            print("No data to export to PDF")
            return filepath
            
        # Create document
        doc = SimpleDocTemplate(str(filepath), pagesize=A4, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        )
        
        # Build story
        story = []
        
        # Title
        title = f"Data Report: {topic}" if topic else "Data Export Report"
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))
        
        # Metadata
        metadata = self._prepare_metadata(data, topic)
        meta_text = f"""<b>Export Details:</b><br/>
        Generated: {metadata['export_timestamp']}<br/>
        Total Records: {metadata['total_records']}<br/>
        Topic: {topic or 'General Data'}<br/>
        Source: MAN Scraper Suite
        """
        story.append(Paragraph(meta_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Prepare table data
        if data:
            headers = list(data[0].keys())
            table_data = [headers]
            
            for row in data[:50]:  # Limit to first 50 records for PDF
                row_data = []
                for header in headers:
                    cell_value = str(row.get(header, ''))[:100]  # Limit cell content length
                    row_data.append(cell_value)
                table_data.append(row_data)
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Data styling
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                
                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(table)
            
            if len(data) > 50:
                story.append(Spacer(1, 12))
                story.append(Paragraph(f"<i>Note: Showing first 50 of {len(data)} total records</i>", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ PDF Exported: {filepath} ({len(data)} records)")
        return filepath
