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


	cv2.imwrite('%s_channel0.jpg'%filename,df_tmp[:,:,0])	
	cv2.imwrite('%s_channel1.jpg'%filename,df_tmp[:,:,1])

	deepflow_datastruct = [channel0_min,channel0_max,channel1_min,channel1_max]

	np.save('%s_scalingcoeff'%filename,deepflow_datastruct)

def read_deepflow_compressed(filename):
	deepflow_datastruct = np.load('%s_scalingcoeff.npy'%filename)

	channel0 = cv2.imread('%s_channel0.jpg'%filename)	
	channel1 = cv2.imread('%s_channel1.jpg'%filename)

	deepflow_results = np.zeros((channel0.shape[0],channel0.shape[1],2))
	deepflow_results[:,:,0] = channel0[:,:,0]
	deepflow_results[:,:,1] = channel1[:,:,0]
	
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

print("shape", deepflow_res.shape[0], deepflow_res.shape[1])

diff = np.abs(deepflow_results - deepflow_res)


cnt = 0
for r in range(0,diff.shape[0]):
	for c in range(0,diff.shape[1]):

			if (diff[r,c,0] > 0.5 or diff[r,c,1] > 0.5):
				cnt = cnt + 1


mean = np.mean(np.mean(np.mean(diff)))
maxerr = np.max(np.max(np.max(diff)))

diff_reshaped = np.reshape(diff,(diff.shape[0]*diff.shape[1]*diff.shape[2]))
standard_deviation = np.std(diff_reshaped)

print("mean error = {}".format(mean))
print('max error = {}'.format(maxerr))
print('std dev = {}'.format(standard_deviation))
print('no of entries with difference great than 0.5= {}'.format(cnt))


'''
deepflow_datastruct = np.load('ruff.npy')
deepflow_res = deepflow_datastruct[0]
print(deepflow_res.shape)
'''



