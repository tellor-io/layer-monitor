import matplotlib.pyplot as plt
import csv
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer

def generate_charts(csv_file):
    block_heights = []
    block_sizes = []
    block_times = []
    num_validators = []
    num_txs = []

    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            block_heights.append(int(row['height']))
            block_sizes.append(int(row['block_size']))
            
            time_since_prev_block = row.get('time_since_prev_block')
            if time_since_prev_block is not None:
                block_times.append(float(time_since_prev_block))
            else:
                block_times.append(0.0)  # or any default value you prefer
            
            num_validators.append(int(row['num_validators']))
            num_txs.append(int(row['num_txs']))

    plt.figure(figsize=(10, 6))
    plt.plot(block_heights, block_sizes)
    plt.xlabel("Block Height")
    plt.ylabel("Block Size (bytes)")
    plt.title("Block Size vs Block Height")
    plt.savefig("charts/block_size.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(block_heights, block_times)
    plt.xlabel("Block Height")
    plt.ylabel("Block Time (s)")
    plt.title("Block Time vs Block Height")
    plt.savefig("charts/block_time.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(block_heights, num_validators)
    plt.xlabel("Block Height")
    plt.ylabel("Number of Validators")
    plt.title("Number of Validators vs Block Height")
    plt.savefig("charts/num_validators.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(block_heights, num_txs)
    plt.xlabel("Block Height")
    plt.ylabel("Number of Transactions")
    plt.title("Number of Transactions vs Block Height")
    plt.savefig("charts/num_txs.png")
    plt.close()

def generate_charts_and_pdf(csv_file, pdf_file):
    block_heights = []
    block_sizes = []
    block_times = []
    num_validators = []
    num_txs = []

    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            block_heights.append(int(row['height']))
            block_sizes.append(int(row['block_size']))
            
            time_since_prev_block = row.get('time_since_prev_block')
            if time_since_prev_block is not None:
                block_times.append(float(time_since_prev_block))
            else:
                block_times.append(0.0)  # or any default value you prefer
            
            num_validators.append(int(row['num_validators']))
            num_txs.append(int(row['num_txs']))

    # Calculate statistics
    block_size_stats = calculate_stats(block_sizes)
    block_time_stats = calculate_stats(block_times)
    num_validators_stats = calculate_stats(num_validators)
    num_txs_stats = calculate_stats(num_txs)

    # Format statistics to 2 decimal places
    def format_stats(stats):
        return {k: f"{v:.2f}" for k, v in stats.items()}

    block_size_stats = format_stats(block_size_stats)
    block_time_stats = format_stats(block_time_stats)
    num_validators_stats = format_stats(num_validators_stats)
    num_txs_stats = format_stats(num_txs_stats)

    # Create a PDF document
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    elements = []

    # Add charts to the PDF
    chart_files = [
        ("charts/block_size.png", "Block Size (bytes)"),
        ("charts/block_time.png", "Block Time (s)"),
        ("charts/num_validators.png", "Number of Validators"),
        ("charts/num_txs.png", "Number of Transactions")
    ]

    for chart_file, ylabel in chart_files:
        img = Image(chart_file, width=400, height=300)
        elements.append(img)
        elements.append(Spacer(1, 12))

    # Add statistics table to the PDF
    data = [
        ['Metric', 'Mean', 'Median', 'Range', 'Std Dev'],
        ['Block Size (bytes)', block_size_stats['mean'], block_size_stats['median'], block_size_stats['range'], block_size_stats['std']],
        ['Block Time (s)', block_time_stats['mean'], block_time_stats['median'], block_time_stats['range'], block_time_stats['std']],
        ['Num Vals', num_validators_stats['mean'], num_validators_stats['median'], num_validators_stats['range'], num_validators_stats['std']],
        ['Num Txs', num_txs_stats['mean'], num_txs_stats['median'], num_txs_stats['range'], num_txs_stats['std']]
    ]
    table = Table(data, colWidths=[1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(Spacer(1, 12))  # Add space before the table
    elements.append(table)
    elements.append(Spacer(1, 12))  # Add space after the table

    # Build the PDF
    doc.build(elements)

def calculate_stats(data):
    return {
        'mean': np.mean(data),
        'median': np.median(data),
        'range': np.max(data) - np.min(data),
        'std': np.std(data)
    }

def main():
    csv_file = 'data/chain_data.csv'
    pdf_file = 'report.pdf'
    generate_charts(csv_file)
    generate_charts_and_pdf(csv_file, pdf_file)

if __name__ == '__main__':
    main()