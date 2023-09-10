import os

# 获取当前目录作为文件夹路径
folder_path = os.getcwd()

# 获取当前目录下所有以".txt"结尾的文件
txt_files = [file for file in os.listdir(folder_path) if file.endswith(".txt")]

# 保存所有文件的第一列中以".gene"结尾的字符
gene_names = []

# 遍历每个文件并提取目标内容
for txt_file in txt_files:
    file_path = os.path.join(folder_path, txt_file)
    with open(file_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            columns = line.strip().split("\t")  # 假设数据以制表符分隔
            if columns and columns[0].endswith(".gene"):
                gene_name = columns[0].split(".gene")[0]  # 提取.gene前面的字符
                gene_names.append(gene_name)

# 匹配结果与FASTA文件
fa_file = "/home/hly/zcz/blast/20230908_qPCR_Primer_design/epcr/Ghirsutum_TM-1_WHU_standard.gene.cds.fa"  # 请替换为你的fa文件路径

matching_sequences = []

with open(fa_file, "r") as fa:
    current_sequence = ""
    for line in fa:
        if line.startswith(">"):
            # 如果是标题行，则保存之前的序列（如果有的话）
            if current_sequence:
                matching_sequences.append(current_sequence)
            current_sequence = line.strip()  # 保存新的标题行
        else:
            # 如果不是标题行，则将行添加到当前序列
            current_sequence += line.strip()

# 检查每个序列是否匹配gene名字
matching_lines = []
for sequence in matching_sequences:
    for gene_name in gene_names:
        if gene_name in sequence:
            # 删除多余的信息，只保留 [mRNA] locus= 之后的内容
            sequence_template = sequence.split("[mRNA] locus=")[-1]
            # 找到第三个冒号后的字符
            third_colon_index = sequence_template.find(":", sequence_template.find(":", sequence_template.find(":") + 1) + 1)
            if third_colon_index != -1:
                sequence_template = sequence_template[third_colon_index + 2:]  # 从第三个冒号后的第二个字符开始截取
            matching_lines.append(f"SEQUENCE_ID={gene_name}\nSEQUENCE_TEMPLATE={sequence_template}\n")

output_file = "matching_sequences.fa"  # 指定输出文件名
with open(output_file, "w") as output:
    for i, match_sequence in enumerate(matching_lines):
        output.write(match_sequence)
        if (i + 1) % 1 == 0 and (i + 1) != len(matching_lines):
            output.write("=\n")  # Add "=" after every second line, except for the last pair

# Add "=" on a new line at the end of the file
with open(output_file, "a") as output:
    output.write("=\n")

print(f"匹配的序列已保存到 {output_file}")
