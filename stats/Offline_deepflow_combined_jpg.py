import numpy as np
import cv2

import copy

def write_deepflow_compressed(deepflow_results, filename):
	
	df_tmp = copy.deepcopy(deepflow_results)

	channel0_min = np.min(np.min(df_tmp[:,:,0]))
	channel0_max = np.max(np.max(df_tmp[:,:,0]))

	channel1_min = np.min(np.min(df_tmp[:,:,1]))
	channel1_max = np.max(np.max(df_tmp[:,:,1]))

	channel0_range = channel0_max - channel0_min
	channel1_range = channel1_max - channel1_min

	df_tmp[:,:,0] = np.round(255.0 * (df_tmp[:,:,0] - channel0_min)/channel0_range)
	df_tmp[:,:,1] = np.round(255.0 * (df_tmp[:,:,1] - channel1_min)/channel1_range)

	df_tmp = df_tmp.astype(np.uint8)

	# just adding extra redundant channel (R,G,B) to write colored JPEG	
	df_new = np.zeros((deepflow_results.shape[0],deepflow_results.shape[1],3),dtype=np.uint8)
	df_new[:,:,0] = df_tmp[:,:,0]
	df_new[:,:,1] = df_tmp[:,:,1]


	cv2.imwrite('%s_channels.jpg'%filename,df_new)

	deepflow_datastruct = [channel0_min,channel0_max,channel1_min,channel1_max]

	np.save('%s_scalingcoeff'%filename,deepflow_datastruct)

def read_deepflow_compressed(filename):
	deepflow_datastruct = np.load('%s_scalingcoeff.npy'%filename)

	channels = cv2.imread('%s_channels.jpg'%filename)

	deepflow_results = np.zeros((channels.shape[0],channels.shape[1],2))
	deepflow_results[:,:,0] = channels[:,:,0] 
	deepflow_results[:,:,1] = channels[:,:,1]
	
	channel0_min = deepflow_datastruct[0]
	channel0_max = deepflow_datastruct[1]

	channel1_min = deepflow_datastruct[2]
	channel1_max = deepflow_datastruct[3]

	channel0_range = channel0_max - channel0_min
	channel1_range = channel1_max - channel1_min

	deepflow_results = deepflow_results.astype(np.float32)

	deepflow_results[:,:,0] = (((deepflow_results[:,:,0] * channel0_range)/255.0) + channel0_min)
	deepflow_results[:,:,1] = (((deepflow_results[:,:,1] * channel1_range)/255.0) + channel1_min)

	return deepflow_results

deepflow_results = np.load('outfile1192907104984426332_1192907105367188995.npz')

deepflow_results = deepflow_results['deepflow']




write_deepflow_compressed(deepflow_results,'ruff')
deepflow_res = read_deepflow_compressed('ruff')

diff = np.abs(deepflow_results - deepflow_res)


cnt = 0
for r in range(0,diff.shape[0]):
	for c in range(0,diff.shape[1]):
		for cols in range(0,diff.shape[2]):
			if (diff[r,c,cols] > 1.0):
				cnt = cnt + 1


mean = np.mean(np.mean(np.mean(diff)))
maxerr = np.max(np.max(np.max(diff)))

print("mean error = {}".format(mean))
print('max error = {}'.format(maxerr))
print('no of entries with difference great than 1.0= {}'.format(cnt))


'''
deepflow_datastruct = np.load('ruff.npy')
deepflow_res = deepflow_datastruct[0]
print(deepflow_res.shape)
'''



