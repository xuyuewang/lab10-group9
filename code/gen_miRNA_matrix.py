# modify for all cancer types with more labels.
import pandas as pd 
import hashlib
import os 
from utils import logger
def file_as_bytes(file):
    with file:
        return file.read()

def extractMatrix(dirname):
	'''
	return a dataframe of the miRNA matrix, each row is the miRNA counts for a file_id

	'''
	count = 0

	miRNA_data = []
	for idname in os.listdir(dirname):
		# list all the ids 
		if idname.find("-") != -1:
			idpath = dirname +"/" + idname

			# all the files in each id directory
			for filename in os.listdir(idpath):
				# check the miRNA file
				if filename.find("-") != -1:

					filepath = idpath + "/" + filename
					df = pd.read_csv(filepath,sep="\t")
					# columns = ["miRNA_ID", "read_count"]
					if count ==0:
						# get the miRNA_IDs 
						miRNA_IDs = df.miRNA_ID.values.tolist()

					id_miRNA_read_counts = [idname] + df.read_count.values.tolist()
					miRNA_data.append(id_miRNA_read_counts)


					count +=1
					# print (df)
	columns = ["file_id"] + miRNA_IDs
	df = pd.DataFrame(miRNA_data, columns=columns)
	return df

def extractLabel(inputfile):
	df = pd.read_csv(inputfile, sep=",")
	columns = ['file_id','label_primary','label_sample']
	return (df[columns])

if __name__ == '__main__':


	data_dir ="/home/amber/Documents/ee542-lab10-group9/data/"
	# Input directory and label file. The directory that holds the data. Modify this when use.
	dirname = data_dir + "miRNA"
	label_file = data_dir + "file_label.csv"
	
	#output file
	outputfile = data_dir + "miRNA_matrix.csv"

	# extract data
	matrix_df = extractMatrix(dirname)
	label_df = extractLabel(label_file)

	#merge the two based on the file_id
	result = pd.merge(matrix_df, label_df, on='file_id', how="left")
	#print(result)

	#save data
	result.to_csv(outputfile, index=False)
	#print (labeldf)

 




