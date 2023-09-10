import re
import argparse
import subprocess
import os

def run_primer3(input_sequence_file, output_primer_file):
    # 构建 primer3_core 命令
    primer3_command = [
        "primer3_core",
        "--p3_settings_file=primer3_config.txt",
        f"--output={output_primer_file}",
        input_sequence_file,
    ]

    # 运行 primer3_core 命令
    try:
        subprocess.run(primer3_command, check=True)
        print(f"primer3_core 已完成并将结果保存到 {output_primer_file}")
    except subprocess.CalledProcessError as e:
        print(f"primer3_core 运行失败：{e}")

def extract_and_format_primers(primer_output_file, epcr_input_file):
    # 打开 primer3 输出文件并读取内容
    with open(primer_output_file, 'r') as file:
        file_content = file.read()

    # 使用正则表达式提取所需的信息
    sequence_id_matches = re.findall(r'SEQUENCE_ID=(.*?)\n', file_content)
    primer_left_0_sequence_matches = re.findall(r'PRIMER_LEFT_0_SEQUENCE=(.*?)\n', file_content)
    primer_right_0_sequence_matches = re.findall(r'PRIMER_RIGHT_0_SEQUENCE=(.*?)\n', file_content)
    primer_right_1_sequence_matches = re.findall(r'PRIMER_RIGHT_1_SEQUENCE=(.*?)\n', file_content)
    primer_left_1_sequence_matches = re.findall(r'PRIMER_LEFT_1_SEQUENCE=(.*?)\n', file_content)
    primer_right_2_sequence_matches = re.findall(r'PRIMER_RIGHT_2_SEQUENCE=(.*?)\n', file_content)
    primer_left_2_sequence_matches = re.findall(r'PRIMER_LEFT_2_SEQUENCE=(.*?)\n', file_content)

    # 准备 e-PCR 输入格式的数据
    output_lines = []
    for i in range(len(sequence_id_matches)):
        sequence_id = sequence_id_matches[i]
        primer_left_0_sequence = primer_left_0_sequence_matches[i]
        primer_right_0_sequence = primer_right_0_sequence_matches[i]
        primer_right_1_sequence = primer_right_1_sequence_matches[i]
        primer_left_1_sequence = primer_left_1_sequence_matches[i]
        primer_right_2_sequence = primer_right_2_sequence_matches[i]
        primer_left_2_sequence = primer_left_2_sequence_matches[i]

        # 在基因名字后面添加 -1、-2、-3
        output_line_0 = f"{sequence_id}-1\t{primer_left_0_sequence}\t{primer_right_0_sequence}\t"
        output_line_1 = f"{sequence_id}-2\t{primer_left_1_sequence}\t{primer_right_1_sequence}\t"
        output_line_2 = f"{sequence_id}-3\t{primer_left_2_sequence}\t{primer_right_2_sequence}\t"

        output_lines.extend([output_line_0, output_line_1, output_line_2])

    # 在输出的最后添加一个空白行
    output_lines.append('')

    # 将结果输出到 e-PCR 输入文件
    with open(epcr_input_file, 'w') as output_file:
        for line in output_lines:
            output_file.write(line + '\n')
    print(f"已将 e-PCR 输入保存到 {epcr_input_file}")

def run_epcr(input_file, output_file, target_genome_file):
    # 构建 e-PCR 命令
    epcr_command = [
        "e-PCR",  # 假定系统中可以直接运行 e-PCR
        "-w9",
        "-f1",
        "-m100",
        "-o",
        output_file,
        input_file,
        "D=50-500",
        target_genome_file,
        "N=1",
        "G=1",
        "T=3",
    ]

    # 运行 e-PCR 命令
    try:
        subprocess.run(epcr_command, check=True)
        print(f"e-PCR 已完成并将结果保存到 {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"e-PCR 运行失败：{e}")

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Run primer3_core and e-PCR with specified input and output files.")
    parser.add_argument("-o", "--output_file", default="epcr_output.txt", help="Output file for e-PCR results")
    parser.add_argument("-g", "--target_genome_file", default="/home/hly/zcz/blast/20230908_qPCR_Primer_design/epcr/Ghirsutum_TM-1_WHU_standard.gene.cds.fa", help="Path to target genome sequence file")
    args = parser.parse_args()

    # 检查 primer3_core 输出文件是否存在，如果不存在则运行 primer3_core
    primer_output_file = "primer_output.txt"
    if not os.path.exists(primer_output_file):
        run_primer3("matching_sequences.fa", primer_output_file)

    # 提取并格式化 primer 结果
    epcr_input_file = "epcr_input.txt"
    extract_and_format_primers(primer_output_file, epcr_input_file)

    # 运行 e-PCR
    run_epcr(epcr_input_file, args.output_file, args.target_genome_file)
