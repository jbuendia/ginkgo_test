## This is a pipeline that takes as input fastq files and outputs a vcf file ###

import subprocess

def check_quality(fastq1, fastq2, output_fastqc):
    subprocess.run(['mkdir', output_fastqc])
    subprocess.run(['fastqc', '-o', output_fastqc, fastq1, fastq2])
    print('FASTQC run complete...')

def align_reads(fastq1, fastq2, reference_genome, output_sam, output_bam):
    # Create index
    subprocess.run(['bwa', 'index', reference_genome])
    print('Reference index created successfully...')
    # Align reads using BWA
    subprocess.run(['bwa', 'mem', '-t', '4', reference_genome, fastq1, fastq2], stdout=open(output_sam, 'w'))
    print('Alignment using BWA completed...')
    # Convert SAM to BAM
    subprocess.run(['samtools', 'view', '-b', '-o', output_bam, output_sam])
    print('BAM file created successfully...')

def sort_and_index_bam(input_bam):
    # Sort BAM file
    sorted_bam = input_bam.replace('.bam', '_sorted.bam')
    subprocess.run(['samtools', 'sort', '-o', sorted_bam, input_bam])
    print('BAM file sorted successfully...')

    # Here we can do mark duplicates using Picard
    # not doing it here in the interest of time and
    # since I don't have Java/Picard installed on my personal computer

    # Index sorted BAM file
    subprocess.run(['samtools', 'index', sorted_bam])
    print('Sorted BAM file indexed successfully...')

def call_variants(input_bam, reference_genome, output_vcf):
    # Call variants using freebayes
    subprocess.run(['freebayes', '-f', reference_genome, input_bam], stdout=open(output_vcf, 'w'))
    print('Variant calling using Freebayes completed...')

def main():
  """Runs the variant calling pipeline."""
  fastq1_path = 'data/sample.R1.paired.fq.gz'
  fastq2_path = 'data/sample.R2.paired.fq.gz'
  reference_genome_path = 'data/MN908947.3.fasta'

  # Paths to output files
  output_fastqc_path = 'out/fastqc/'
  output_sam_path = 'out/aligned_reads.sam'
  output_bam_path = 'out/aligned_reads.bam'
  output_vcf_path = 'out/variants.vcf'

  # Step 0: Check read quality using FASTQC
  check_quality(fastq1_path, fastq2_path, output_fastqc_path)

  # Step 1: Align reads
  align_reads(fastq1_path, fastq2_path, reference_genome_path, output_sam_path, output_bam_path)

  # Step 2: Sort and index BAM file
  sort_and_index_bam(output_bam_path)

  # Step 3: Call variants
  call_variants(output_bam_path.replace('.bam', '_sorted.bam'), reference_genome_path, output_vcf_path)

  print("Variant calling pipeline completed successfully!")

if __name__ == "__main__":
  main()