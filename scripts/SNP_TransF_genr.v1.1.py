import argparse
import subprocess
import os
import gzip
import shutil

def process_snp_data(snp_data):
    snp_dict = {}
    for snp in snp_data:
        snp_info = snp.split()
        gene_info = snp_info[0]
        p_value = float(snp_info[1])

        chromosome, position, *_ = gene_info.split('_')
        position = int(position)

        if position in snp_dict:
            if p_value < snp_dict[position][0]:
                snp_dict[position] = (p_value, chromosome)
        else:
            snp_dict[position] = (p_value, chromosome)

    filtered_snps = []
    prev_position = None
    for position, (p_value, chromosome) in sorted(snp_dict.items()):
        if prev_position is None or position - prev_position >= 500000:
            filtered_snps.append((chromosome, position, p_value))
        elif p_value < filtered_snps[-1][2]:
            filtered_snps[-1] = (chromosome, position, p_value)
        prev_position = position

    return filtered_snps

# 读取.blocks.gz文件并提取前五个数
def read_blocks_file(blocks_file):
    data = []
    with open(blocks_file, 'r') as file:
        for line in file:
            # 分割行并提取前五个数
            row_data = line.strip().split()
            first_five_numbers = row_data[:5]
            data.append(first_five_numbers)
    return data

def extract_genes_from_gff(gff_file, chromosome, start, end):
    genes_info = []
    with open(gff_file, 'r') as file:
        for line in file:
            if line.startswith('#'):
                continue
            cols = line.strip().split('\t')
            if cols[0] == chromosome and int(cols[3]) <= end and int(cols[4]) >= start:
                if cols[2] == 'gene':
                    gene_name = cols[8].split(';')[0].split('=')[1]
                    genes_info.append((gene_name, line.strip()))
    return genes_info

def preprocess_numbers(number_str):
    num = int(number_str)
    if 1 <= num <= 13:
        return 'A' + str(num).zfill(2)
    elif 14 <= num <= 26:
        return 'D' + str(num - 13).zfill(2)
    else:
        return str(num)

def main():
    input_file = "SNP_block.txt"
    output_folder = "Position"

    # Check if the output folder already exists
    if os.path.exists(output_folder):
        # If the folder exists, remove all files in it
        for file_name in os.listdir(output_folder):
            file_path = os.path.join(output_folder, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        # If the folder does not exist, create it
        os.makedirs(output_folder)

    with open(input_file, "r") as f:
        lines = f.readlines()

    for line in lines:
        columns = line.strip().split()
        num1, num2, num3, *_ = columns
        identifier = preprocess_numbers(int(num1))

        # Check if the output file already exists, and skip if it does
        output_file = os.path.join(output_folder, f"{identifier}_{num2}_{num3}.txt")
        if os.path.exists(output_file):
            continue

        # Write the data to the output file
        with open(output_file, "a") as f:
            f.write(f"{identifier}\t{num2}\t{num3}\n")

if __name__ == "__main__":
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Process SNP data and extract genes from GFF file.')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input SNP file (txt format)')
    parser.add_argument('-v', '--vcf', type=str, required=True, help='Input VCF file')
    parser.add_argument('-o', '--output_folder', type=str, required=True, help='Output folder to save gene information files')
    parser.add_argument('-g', '--gff_file', type=str, required=True, help='GFF file')

    # Parse the arguments
    args = parser.parse_args()

    # Create the output folder if it doesn't exist
    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)

    # Read SNP data from the input file
    with open(args.input, 'r') as file:
        snp_data = file.read().splitlines()

    # Call the function with the SNP data read from the file
    filtered_snps = process_snp_data(snp_data)

    # Output the results in the desired format
    with open("SNP_500k.txt", 'w') as file:
        for chromosome, position, _ in filtered_snps:
            start_range = max(1, int(position) - 500000)
            end_range = int(position) + 500000
            file.write(f"{chromosome}:{start_range}:{end_range}\n")
    
    # Clear the content of SNP_block.txt before writing new data
    with open("SNP_block.txt", 'w') as snp_block_file:
        snp_block_file.write("")

    # Define the result_file directory
    
    result_file = "LDblock_result"
    if not os.path.exists(result_file):
        os.makedirs(result_file)

    # Create the Block folder if it doesn't exist
    block_folder = "Block"

    if os.path.exists(block_folder):
        # If the folder exists, remove all files in it
        for file_name in os.listdir(block_folder):
            file_path = os.path.join(block_folder, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        # If the folder does not exist, create it
        os.makedirs(block_folder)


    # Execute LDBlockShow for each region in the SNP data
    for chromosome, position, _ in filtered_snps:
        start_range = max(1, int(position) - 500000)
        end_range = int(position) + 500000
        region = f"{chromosome}:{start_range}:{end_range}"
        filename = f"{chromosome}_{start_range}_{end_range}"

        print(f"正在处理：{chromosome} {start_range} {end_range}")

        # Execute LDBlockShow command using subprocess with -InVCF provided through -v argument
        cmd = f"LDBlockShow -InVCF {args.vcf} -OutPut {result_file}/{filename} -Region {region} -OutPng -SeleVar 2"

        # 隐藏LDBlockShow的命令提示输出
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 解压缩.blocks.gz文件
        subprocess.run(f"gunzip {os.path.join(result_file, filename + '.blocks.gz')}", shell=True)

        # 读取解压后的文件并找到与position匹配的行
        matched_lines = []
        with open(os.path.join(result_file, filename + '.blocks'), 'r') as uncompressed_file:
            for line in uncompressed_file:
                if str(position) in line:
                    matched_lines.append(line.strip())

        # 提取匹配行的前五个数并输出
        for matched_line in matched_lines:
            row_data = matched_line.split()
            first_five_numbers = row_data[:5]

            # 保存前五个数到SNP_block.txt
            with open("SNP_block.txt", 'a') as snp_block_file:
                snp_block_file.write(" ".join(first_five_numbers) + "\n")

            # 处理前三个数，以chromosome_num:start_position:end_position形式调用LDBlockShow
            if len(first_five_numbers) >= 3:
                first_three_numbers = first_five_numbers[:3]
                chromosome_num = first_three_numbers[0]
                start_position = int(first_three_numbers[1])
                end_position = int(first_three_numbers[2])

                # 不进行处理，直接使用数字13
                chromosome_num = str(int(chromosome_num))

                # 拼接成正确的格式
                new_region = f"{chromosome_num}:{start_position}:{end_position}"
                new_filename = f"{chromosome_num}_{start_position}_{end_position}"

                # 调用LDBlockShow
                new_cmd = f"LDBlockShow -InVCF {args.vcf} -OutPut {block_folder}/{new_filename} -Region {new_region} -OutPng -SeleVar 2"
                subprocess.run(new_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


        # 调用extract_genes_from_gff函数提取基因信息
        with open("SNP_block.txt", 'r') as snp_block_file:
            for line in snp_block_file:
                cols = line.strip().split()
                if len(cols) >= 3:
                    chromosome = preprocess_numbers(cols[0])  # 处理第一个数
                    start_position = int(cols[1])
                    end_position = int(cols[2])

                    genes_info_in_range = extract_genes_from_gff(args.gff_file, chromosome, start_position, end_position)

                    if genes_info_in_range:
                        # Save gene information to output file
                        output_file_path = f"{args.output_folder}/{chromosome}_{start_position}_{end_position}_genes.txt"
                        with open(output_file_path, 'w') as output_file:
                            for gene_info in genes_info_in_range:
                                output_file.write(f"{gene_info[0]}\t{gene_info[1]}\n")


    main()
    
# 删除LDblock_result文件夹
shutil.rmtree("LDblock_result")
