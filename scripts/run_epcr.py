import argparse
import subprocess

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
    # 从命令行参数中读取输出文件和目标基因组文件路径
    parser = argparse.ArgumentParser(description="Run e-PCR with specified input and output files.")
    parser.add_argument("-o", "--output_file", help="Output file for e-PCR results")
    parser.add_argument("-g", "--target_genome_file", help="Path to target genome sequence file")
    args = parser.parse_args()

    # 读取输入文件 epcr_input.txt
    input_file = "epcr_input.txt"

    # 检查参数并运行 e-PCR
    if args.output_file and args.target_genome_file:
        run_epcr(input_file, args.output_file, args.target_genome_file)
    else:
        print("请提供输出文件 (-o) 和目标基因组序列文件 (-g) 的路径。")
