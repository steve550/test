import numpy as np
import cv2

def write_deepflow_compressed(deepflow_results, filename):
	
	channel0_min = np.min(np.min(deepflow_results[:,:,0]))
	channel0_max = np.max(np.max(deepflow_results[:,:,0]))

	channel1_min = np.min(np.min(deepflow_results[:,:,1]))
	channel1_max = np.max(np.max(deepflow_results[:,:,1]))

	channel0_range = channel0_max - channel0_min
	channel1_range = channel1_max - channel1_min

	deepflow_results[:,:,0] = np.round(255.0 * (deepflow_results[:,:,0] - channel0_min)/channel0_range)
	deepflow_results[:,:,1] = np.round(255.0 * (deepflow_results[:,:,1] - channel1_min)/channel1_range)

	deepflow_results = deepflow_results.astype(np.uint8)

	# just adding extra redundant channel (R,G,B) to write colored JPEG	
	deepflow_res = np.zeros((deepflow_results.shape[0],deepflow_results.shape[1],3),dtype=np.uint8)
	deepflow_res[:,:,0] = deepflow_results[:,:,0]
	deepflow_res[:,:,1] = deepflow_results[:,:,1]


	cv2.imwrite('%s_channels.jpg'%filename,deepflow_res)

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

print(deepflow_results.shape)

print(deepflow_results[1000,1000,0])
print(deepflow_results[1500,500,1])

write_deepflow_compressed(deepflow_results,'ruff')
deepflow_res = read_deepflow_compressed('ruff')

print(deepflow_res[1000,1000,0])
print(deepflow_res[1500,500,1])
'''
deepflow_datastruct = np.load('ruff.npy')
deepflow_res = deepflow_datastruct[0]
print(deepflow_res.shape)
'''



