# qPCR_pprimer_desigmed
### GWAS关联分析找到显著位点

###利用SNP_TransF_genr.v1.1.py 脚本找到多年重复的显著位点的目标基因
python3 SNP_TransF_genr.v1.1.py -i SNP.txt -v test.vcf -o output -g ref.gff



###利用 Extract_seq.py 找到gff文件中目标基因的序列并将其整理成primer3的输入文件
python3 Extract_seq.py


###若是在线网站设计引物则可以将引物信息整理成epcr格式运行 run_epcr.py进行验证
python3 run_epcr.py


### 利用primer3_with_ePCR_validation.py调用primer3_core和epcr 设计引物并进行引物验证
python3 primer3_with_ePCR_validation.py

