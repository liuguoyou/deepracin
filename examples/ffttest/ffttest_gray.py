import deepracin as dr
from scipy import misc
import numpy as np
from skimage import io

preferred_platform_name = 'Mesa'

with dr.Environment(preferred_platform_name) as env:
    # Properties
    # If true, all debug outputs are printed (Default: False)
    env.debuginfo = True

    # If true, the overall CPU runtimes are profiled and printed (Default: False)
    env.profileCPU = True

    # If true, the GPU kernel runtimes are profiled and printed (Default: False)
    env.profileGPU = True

    # If true, all outputs are supressed (Default: True)
    env.silent = True

    # If not set, a temporary folder will be created in location depending on system
    # Folder is used to store kernels, ptx, and (if model is exported) the exported model)
    env.model_path = 'model/'

# Create empty graph
graph = env.create_graph(interface_layout='HWC')

# Fill graph
# Feed node - Will be fed with data for each graph application
#feed_node = dr.feed_node(graph, shape=(497, 303, 1))

feed_node = dr.feed_node(graph, shape=(224, 224, 3))

r, g, b = [feed_node[0:224, 0:224, 0] - 123.68,
            feed_node[0:224, 0:224, 1] - 116.779,
            feed_node[0:224, 0:224, 2] - 103.939]

concat = dr.Concat([b, g, r], 2)

###

###

rgb_to = dr.RGB_to_gray(concat)

# create FFT node
ffttest = dr.FFT(rgb_to)

# Mark output nodes (determines what dr.apply() returns)
dr.mark_as_output(ffttest)

# Print graph to console
dr.print_graph(graph)

# Save deepracin graph
dr.save_graph(graph,env.model_path)

dr.prepare(graph)

image_paths = ['tiger.png']

for path in image_paths:

    # Feed Input
    img = io.imread(path)
    data = np.array(img).astype(np.float32)
    dr.feed_data(feed_node,data)

    # Apply graph - returns one numpy array for each node marked as output
    fftout = dr.apply(graph)
    dat = np.array(fftout[0]).astype(np.float32)
    io.imshow(dat)
    io.show()