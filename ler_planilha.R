getwd()
setwd('O:/python_unifesp_sandra')

library(openxlsx)

planilha <- read.csv2("planilha_scrap_dados.csv", header = TRUE, sep = ',')

write.xlsx(planilha, "planilha_final.xlsx")
