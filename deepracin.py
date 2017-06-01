from ctypes import *
import platform
import numpy as np
import tempfile
import shutil
import errno
import os
import sys
dir = os.path.dirname(__file__)
filename = os.path.join(dir, '/relative/path/to/file/you/want')

if platform.system()=='Windows':
    filename = os.path.join(dir, '../Release/deepracin')
elif platform.system()=='Linux':
    filename = os.path.join(dir, '../libdeepracin.so')

else:
    print("Not a known Platform!")
    exit()
lib = cdll.LoadLibrary(filename)


class Shape2(Structure):
    _fields_ = [("s0", c_int), ("s1", c_int)]


class Shape3(Structure):
    _fields_ = [("s0", c_int), ("s1", c_int), ("s2", c_int)]


class Shape4(Structure):
    _fields_ = [("s0", c_int), ("s1", c_int), ("s2", c_int), ("s3", c_int)]


elemwise_2op_dict = { 'Add' : 0,
             'Sub': 1,
             'Mul': 2,
             'Div': 3,
             'Pow': 4}

elemwise_1op_dict = { 'AddS' : 0,
             'SubS': 1,
             'MulS': 2,
             'DivS': 3,
             'Log': 4,
             'Exp': 5,
             'Sqrt': 6,
             'Fill': 7,
             'PowS': 8}

act_dict = { 'linear' : 0,
             'relu': 1}

pool_dict = { 'max' : 0,
             'average': 1}

us_dict = { 'max' : 0,
             'average': 1}

lc_dict = { 'max' : 0,
             'average': 1}

norm_dict = { 'max' : 0,
             'average': 1}


class Node:
    def __init__(self, ptr, graph, desc, params, variables=None):
        self.ptr = ptr
        self.out_shape = [0, 0, 0]
        self.graph = graph
        self.shape = [-1, -1, -1]
        self.desc = desc
        self.params = params
        self.variables = variables
        graph.nodes.append(self)

    def __add__(self, other: float):
        if isinstance(other,float):
            return Add_Scalar(self, other)
        elif isinstance(other,Node):
            return Add(self, other)
        else:
            return NotImplemented

    def __sub__(self, other: float):
        if isinstance(other,float):
            return Sub_Scalar(self, other)
        elif isinstance(other,Node):
            return Sub(self, other)
        else:
            return NotImplemented

    def __mul__(self, other: float):
        if isinstance(other,float):
            return Mul_Scalar(self, other)
        elif isinstance(other,Node):
            return Mul(self, other)
        else:
            return NotImplemented

    def __rdiv__(self, other: float):
        if isinstance(other,float):
            return Div_Scalar(self, other)
        elif isinstance(other,Node):
            return Div(self, other)
        else:
            return NotImplemented

    def __pow__(self, power, modulo=None):
        if isinstance(power,float):
            return Pow_Scalar(self, power)
        elif isinstance(power,Node):
            return Pow(self, power)
        else:
            return NotImplemented

    def __getitem__(self, item):
        slices = None
        if isinstance(item, tuple):
            if all((type(i) is slice or type(i) is int) for i in item) and len(item) == 3:
                slices = [item[0], item[1], item[2]]

        if slices is not None:
            for k,i in enumerate(slices):
                if isinstance(i, int):
                    slices[k] = slice(i, i+1, None)

        if slices is None or any((i.step is not None or i.start is None) for i in slices):
            sys.exit("DR Error: Way of indexing not allowed!")


        origin = [slices[0].start,slices[1].start,slices[2].start]
        shape = [slices[0].stop-slices[0].start,slices[1].stop-slices[1].start,slices[2].stop-slices[2].start]

        print("getitem test: ",origin,shape)
        return Slice(self,origin,shape)


class Graph:
    def __init__(self,id, layout):
        self.ptr = lib.dR_NewGraph()
        self.num_outputs = 0
        self.outnodes = []
        self.id = id
        self.layout = layout
        self.nodes = []
        self.feed_nodes = []
        self.model_path = None


class Env:
    def __init__(self, preferred_platform=''):
        self.preferred_platform_name = preferred_platform
        self.silent = True
        self.debuginfo = False
        self.profileCPU = False
        self.profileGPU = False
        self.tmp_path = tempfile.mkdtemp(prefix='deepracin_')
        self.model_path = self.tmp_path
        self.graphs = []
        self.graph_with_cl_context = -1
        self.id_counter = 0
        return

    def __del__(self):
        try:
            shutil.rmtree(self.tmp_path)  # delete directory
        except OSError as exc:
            if exc.errno != errno.ENOENT:  # ENOENT - no such file or directory
                raise  # re-raise exception
        for i,graph in enumerate(self.graphs):
            if i == len(self.graphs)-1:
                lib.dR_cleanup(graph.ptr,True)
            else:
                lib.dR_cleanup(graph.ptr,False)
        return

env = Env()

# general functions
# Create a new graph
def create_graph(interface_layout):
    graph_id = env.id_counter
    env.id_counter+=1
    graph = Graph(graph_id,interface_layout)
    env.graphs.append(graph)
    return graph

# Create a graph node that can be fed with data
def feed_node(graph, shape):
    if not len(shape)==3:
        sys.exit("DR Error: feed_node()'s shape parameter needs to be a list with 3 ints!")
    if not (isinstance(shape[0], int ) and isinstance(shape[1], int) and isinstance(shape[2], int)):
        sys.exit("DR Error: feed_node()'s shape parameter needs to be a list with 3 ints!")
    dr_shape = [shape[1],shape[0],shape[2]]
    if graph.layout == 'WHC':
        dr_shape = [shape[0],shape[1],shape[2]]
    elif graph.layout == 'CHW':
        dr_shape = [shape[2],shape[1],shape[0]]
    elif graph.layout == 'HWC':
        dr_shape = [shape[1],shape[0],shape[2]]
    else:
        sys.exit("DR Error: Graphs's layout "+graph.layout+" not supported!")
    desc = 'DataFeedNode'
    params = [dr_shape[0],dr_shape[1],dr_shape[2]]
    node = Node(lib.dR_Datafeednode(graph.ptr, Shape3(*dr_shape)),graph,desc,params)
    graph.feed_nodes.append(node)
    return node

# Initializes and prepares a fully defined graph
def prepare(graph):
    ret = True
    if env.graph_with_cl_context == -1:
        platformname = create_string_buffer(str.encode(env.preferred_platform_name))

        if graph.model_path is not None:
            model_path = graph.model_path
        else:
            model_path = env.model_path

        if not os.path.exists(env.model_path):
            os.makedirs(env.model_path)

        model_dir = create_string_buffer(str.encode(model_path))

        lib.dR_config(graph.ptr,platformname,c_bool(env.silent),c_bool(env.debuginfo),c_bool(env.profileGPU),c_bool(env.profileCPU),model_dir)
        ret &= lib.dR_initCL(graph.ptr)
        env.graph_with_cl_context = graph.id

        if not ret:
            sys.exit("DR Error: deepRACIN initCL failed!")
    else:
        lib.dR_getClEnvironmentFrom(graph.ptr, env.graphs[env.graph_with_cl_context].ptr)

    ret &= lib.dR_prepare(graph.ptr)
    for node in graph.outnodes:
        ArrayType = c_int*3
        shape = cast(lib.dR_getOutputShape(node.ptr), POINTER(ArrayType)).contents
        node.out_shape = [shape[0],shape[1],shape[2]]
    for feednode in graph.feed_nodes:
        ArrayType = c_int*3
        shape = cast(lib.dR_getOutputShape(feednode.ptr), POINTER(ArrayType)).contents
        feednode.shape = [shape[0],shape[1],shape[2]]
    if not ret:
        sys.exit("DR Error: deepRACIN prepare failed!")
    return

# Runs the graph - after that, data can be fetched from output arrays
def apply(graph):
    ret = lib.dR_apply(graph.ptr)
    if not ret:
        sys.exit("DR Error: deepRACIN apply failed!")

    memptr = (c_void_p * graph.num_outputs)()
    lib.dR_getOutputBuffers(graph.ptr, memptr)
    out = []
    for i in range(graph.num_outputs):
        out_shape = graph.outnodes[i].out_shape

        dataptr = (c_float * (out_shape[0]*out_shape[1]*out_shape[2]))()
        lib.dR_downloadArray(graph.ptr, "output"+str(i), memptr[i], 0, out_shape[0]*out_shape[1]*out_shape[2]*4, dataptr)
        arr = np.ctypeslib.as_array(dataptr)
        arr = arr.reshape([out_shape[2],out_shape[1],out_shape[0]])
        if graph.layout == 'WHC':
            arr = arr.transpose([2, 1, 0])
        elif graph.layout == 'HWC':
            arr = arr.transpose([1, 2, 0])

        out.append(np.squeeze(arr))
    return out


def mark_as_output(node):
    lib.dR_setAsOutput(node.graph.ptr, node.ptr)
    node.graph.num_outputs += 1
    node.graph.outnodes.append(node)
    return


def feed_data(node, data):
    if not len(data.shape) == 3 :
        sys.exit("DR Error: data fed to a feed_node needs to be an array with 3 dimensions!")
    if data.dtype!=np.float32:
        sys.exit("DR Error: data fed to a feed_node is "+str(data.dtype)+" but needs to be an array of type float32!")

    dr_shape = [data.shape[1],data.shape[0],data.shape[2]]
    if node.graph.layout == 'WHC':
        dr_shape = [data.shape[0],data.shape[1],data.shape[2]]
        data = data.transpose([2, 1, 0]).copy()
    elif node.graph.layout == 'CHW':
        dr_shape = [data.shape[2],data.shape[1],data.shape[0]]
    elif node.graph.layout == 'HWC':
        dr_shape = [data.shape[1],data.shape[0],data.shape[2]]
        data = data.transpose([2, 0, 1]).copy()

    if not dr_shape==node.shape:
        sys.exit("DR Error: data array's dimensions "+str(dr_shape)+" do not match node's dimensions "+str(node.shape)+"!")

    d = np.ctypeslib.as_ctypes(data)
    l = dr_shape[0]*dr_shape[1]*dr_shape[2]
    lib.dR_feedData(node.graph.ptr, node.ptr, d, 0, l)
    return

def load_graph(graph,path : str):
    graph.model_path = path
    num_nodes = c_int(0)
    num_feed_nodes = c_int(0)
    nodesptr = pointer(c_void_p())
    feednodesptr = pointer(c_void_p())
    pathbuf = create_string_buffer(str.encode(path))
    outnodeptr = lib.dR_loadGraph(c_void_p(graph.ptr), pathbuf, byref(nodesptr),byref(num_nodes), byref(feednodesptr),byref(num_feed_nodes))
    if outnodeptr is None:
        sys.exit("DR Error: Model could not be loaded!")

    nodelist = [Node(nodesptr[i],graph, None, None) for i in range(num_nodes.value)]
    feednodelist = [Node(feednodesptr[i],graph, None, None) for i in range(num_feed_nodes.value)]
    graph.feed_nodes = feednodelist

    return nodelist, feednodelist

def load_graph_old(node,path : str):
    maxnumofnodes = 50
    maxnodes = c_int(maxnumofnodes)
    nodeptr = (c_void_p * maxnumofnodes)()
    pathbuf = create_string_buffer(str.encode(path))
    outnodeptr = lib.dR_loadGraph(c_void_p(node.graph.ptr), c_void_p(node.ptr), pathbuf, byref(nodeptr),byref(maxnodes))
    if outnodeptr is None:
        sys.exit("DR Error: Model could not be loaded!")
    outnode = Node(outnodeptr, node.graph, None, None)
    outlist = [Node(nodeptr[i],node.graph, None, None) for i in range(maxnodes.value)]
    return outnode, outlist

def save_graph(graph,path : str):
    pathbuf = create_string_buffer(str.encode(path))
    res = lib.dR_saveGraph(graph.ptr, pathbuf)
    if not res:
        sys.exit("DR Error: Model could not be saved!")
    return

def print_graph(graph):
    lib.dR_printNetObject(graph.ptr, None)

# Specific Node Functions

def Conv2d(input_node : Node, shape : (int, int, int, int), stride : (int, int, int, int), activation : str, weights, biases=None):

    if not (shape[0] == shape[1] and shape[0]%2 == 1):
        sys.exit("DR Error: Conv2d' currently only supports quadratic filter sizes with odd side length!")
    if not (stride[0] == stride[3] == 1 and stride[1] == stride[2]):
        sys.exit("DR Error: Conv2d' currently only strides of from (1,x,x,1)!")
    if biases is not None:
        use_bias = True
    else:
        use_bias = False

    # deepRacin expects [C,F,H,W] conv2d weights
    # transpose [H,W,C,F] -> [C,F,H,W]
    if weights is not None:
        weights = weights.transpose([2,3,0,1]).copy()

    # Description for python structures
    desc = 'Conv2D'
    params = [act_dict[activation], (1 if use_bias else 0),shape[0],shape[1],shape[2],shape[3],stride[0],stride[1],stride[2],stride[3]]
    if use_bias:
        variables = [weights,biases]
    else:
        variables = [weights]

    # Call deepRACIN
    onode = Node(lib.dR_Conv2d(input_node.graph.ptr, input_node.ptr, Shape4(*shape), Shape4(*stride),
                               act_dict[activation], use_bias),input_node.graph, desc, params, variables)
    if weights is not None and biases is not None:
        lib.dR_Conv2d_setVariables(onode.ptr, np.ctypeslib.as_ctypes(weights), np.ctypeslib.as_ctypes(biases))
    elif weights is not None and biases is None:
        lib.dR_Conv2d_setVariables(onode.ptr, np.ctypeslib.as_ctypes(weights), None)
    return onode


'''
Not supported yet!
def Conv2d_Transposed(input_node : Node, shape : (int, int, int, int), stride : (int, int, int, int), activation : str, weights, biases=None):

    if not (shape[0] == shape[1] and shape[0]%2 == 1):
        print("Error: Conv2d_Transposed' currently only supports quadratic filter sizes with odd side length!")
        exit()
    if not (stride[0] == stride[3] == 1 and stride[1] == stride[2]):
        print("Error: Conv2d_Transposed' currently only strides of from (1,x,x,1)!")
        exit()
    if biases is not None:
        use_bias = True
    else:
        use_bias = False
    onode =  Node(lib.dR_Conv2dTransposed(input_node.graph.ptr, input_node.ptr, Shape4(*shape), Shape4(*stride), act_dict[activation], use_bias),input_node.graph)
    if weights is not None and biases is not None:
        lib.dR_Conv2dtransposed_setVariables(onode.ptr, np.ctypeslib.as_ctypes(weights), np.ctypeslib.as_ctypes(biases))
    elif weights is not None and biases is None:
        lib.dR_Conv2dtransposed_setVariables(onode.ptr, np.ctypeslib.as_ctypes(weights), 0)
    return onode
'''

def Fully_Connected(input_node: Node, shape: (int, int), activation: str, weights, biases=None):
    if biases is not None:
        use_bias = True
    else:
        use_bias = False

    # Description for python structures
    desc = 'FullyConnected'
    params = [act_dict[activation], (1 if use_bias else 0),shape[0],shape[1]]
    if use_bias:
        variables = [weights,biases]
    else:
        variables = [weights]

    # Call deepRACIN
    onode = Node(lib.dR_FullyConnected(input_node.graph.ptr, input_node.ptr, Shape2(*shape), act_dict[activation],
                                       use_bias),input_node.graph, desc, params, variables)
    if weights is not None and biases is not None:
        lib.dR_FullyConnected_setVariables(onode.ptr, np.ctypeslib.as_ctypes(weights), np.ctypeslib.as_ctypes(biases))
    elif weights is not None and biases is None:
        lib.dR_FullyConnected_setVariables(onode.ptr, np.ctypeslib.as_ctypes(weights), 0)
    return onode

def Mask_Dependent_Filter(input_node: Node, filter_mask : Node, shape: (int, int, int), filters):
    if input_node.graph != filter_mask.graph:
        sys.exit("DR Error: Inputs for Mask_Dependent_Filter are not in the same graph!")

    # Description for python structures
    desc = 'MaskDependentFilter'
    params = [shape[0],shape[1],shape[2]]
    variables = [filters]

    # Call deepRACIN
    onode = Node(lib.dR_MaskDependentFilter(input_node.graph.ptr, input_node.ptr,filter_mask.ptr,
                                            Shape3(*shape)),input_node.graph, desc, params, variables)
    lib.dR_MaskDependentFilter_setVariables(input_node.graph.ptr, onode, np.ctypeslib.as_ctypes(filters), 0)
    return onode

def Per_Pixel_Filter(input_node: Node, input_filters: Node, shape: (int, int, int, int), stride: (int, int, int, int)):

    # Description for python structures
    desc = 'PPFilter'
    params = [shape[0], shape[1], shape[2], shape[3], stride[0], stride[1], stride[2], stride[3]]

    # Call deepRACIN
    onode = Node(lib.dR_PerPixelFilter(input_node.graph.ptr, input_node.ptr,input_filters.ptr, Shape4(*shape),
                                       Shape4(*stride)),input_node.graph, desc, params)
    return onode

def Add_Scalar(input_node: Node, scalar: float):

    # Description for python structures
    desc = 'ElemWise1Op'
    params = [elemwise_1op_dict['AddS'], scalar]

    # Call deepRACIN
    onode = Node(lib.dR_ElemWise1Operation(input_node.graph.ptr, input_node.ptr,elemwise_1op_dict['AddS'],
                                           c_float(scalar)),input_node.graph, desc, params)
    return onode

def Sub_Scalar(input_node: Node, scalar: float):

    # Description for python structures
    desc = 'ElemWise1Op'
    params = [elemwise_1op_dict['SubS'], scalar]

    # Call deepRACIN
    onode = Node(lib.dR_ElemWise1Operation(input_node.graph.ptr, input_node.ptr,elemwise_1op_dict['SubS'],
                                           c_float(scalar)),input_node.graph, desc, params)
    return onode

def Mul_Scalar(input_node: Node, scalar: float):

    # Description for python structures
    desc = 'ElemWise1Op'
    params = [elemwise_1op_dict['MulS'], scalar]

    # Call deepRACIN
    onode = Node(lib.dR_ElemWise1Operation(input_node.graph.ptr, input_node.ptr,elemwise_1op_dict['MulS'],
                                           c_float(scalar)),input_node.graph, desc, params)
    return onode

def Div_Scalar(input_node: Node, scalar: float):

    # Description for python structures
    desc = 'ElemWise1Op'
    params = [elemwise_1op_dict['DivS'], scalar]

    # Call deepRACIN
    onode = Node(lib.dR_ElemWise1Operation(input_node.graph.ptr, input_node.ptr,elemwise_1op_dict['DivS'],
                                           c_float(scalar)),input_node.graph, desc, params)
    return onode

def Log(input_node: Node):

    # Description for python structures
    scalar = 0.0
    desc = 'ElemWise1Op'
    params = [elemwise_1op_dict['Log']]

    # Call deepRACIN
    onode = Node(lib.dR_ElemWise1Operation(input_node.graph.ptr, input_node.ptr,elemwise_1op_dict['Log'],
                                           c_float(scalar)),input_node.graph, desc, params)
    return onode

def Exp(input_node: Node):
    scalar = 0.0

    # Description for python structures
    desc = 'ElemWise1Op'
    params = [elemwise_1op_dict['Exp']]

    # Call deepRACIN
    onode = Node(lib.dR_ElemWise1Operation(input_node.graph.ptr, input_node.ptr,elemwise_1op_dict['Exp'],
                                           c_float(scalar)),input_node.graph, desc, params)
    return onode

def Sqrt(input_node: Node):
    scalar = 0.0

    # Description for python structures
    desc = 'ElemWise1Op'
    params = [elemwise_1op_dict['Sqrt']]

    # Call deepRACIN
    onode = Node(lib.dR_ElemWise1Operation(input_node.graph.ptr, input_node.ptr,elemwise_1op_dict['Sqrt'],
                                           c_float(scalar)),input_node.graph, desc, params)
    return onode

def Fill(input_node: Node, scalar: float):

    # Description for python structures
    desc = 'ElemWise1Op'
    params = [elemwise_1op_dict['Fill'], scalar]

    # Call deepRACIN
    onode = Node(lib.dR_ElemWise1Operation(input_node.graph.ptr, input_node.ptr,elemwise_1op_dict['Fill'],
                                           c_float(scalar)),input_node.graph, desc, params)
    return onode

def Pow_Scalar(input_node: Node, scalar: float):

    # Description for python structures
    desc = 'ElemWise1Op'
    params = [elemwise_1op_dict['PowS'], scalar]

    # Call deepRACIN
    onode = Node(lib.dR_ElemWise1Operation(input_node.graph.ptr, input_node.ptr,elemwise_1op_dict['PowS'],
                                           c_float(scalar)),input_node.graph, desc, params)
    return onode

def Add(input_node1: Node, input_node2: Node):
    if input_node1.graph != input_node2.graph:
        sys.exit("DR Error: Inputs for Add are not in the same graph!")

    # Description for python structures
    desc = 'ElemWise2Op'
    params = [elemwise_2op_dict['Add']]

    # Call deepRACIN
    onode = Node(lib.dR_ElemWise2Operation(input_node1.graph.ptr, input_node1.ptr, input_node2.ptr,
                                           elemwise_1op_dict['Add']), input_node1.graph, desc, params)
    return onode

def Sub(input_node1: Node, input_node2: Node):
    if input_node1.graph != input_node2.graph:
        sys.exit("DR Error: Inputs for Add are not in the same graph!")

    # Description for python structures
    desc = 'ElemWise2Op'
    params = [elemwise_2op_dict['Sub']]

    # Call deepRACIN
    onode = Node(lib.dR_ElemWise2Operation(input_node1.graph.ptr, input_node1.ptr, input_node2.ptr,
                                           elemwise_1op_dict['Sub']), input_node1.graph, desc, params)
    return onode

def Mul(input_node1: Node, input_node2: Node):
    if input_node1.graph != input_node2.graph:
        sys.exit("DR Error: Inputs for Mul are not in the same graph!")

    # Description for python structures
    desc = 'ElemWise2Op'
    params = [elemwise_2op_dict['Mul']]

    # Call deepRACIN
    onode = Node(lib.dR_ElemWise2Operation(input_node1.graph.ptr, input_node1.ptr, input_node2.ptr,
                                           elemwise_1op_dict['Mul']), input_node1.graph, desc, params)
    return onode

def Div(input_node1: Node, input_node2: Node):
    if input_node1.graph != input_node2.graph:
        sys.exit("DR Error: Inputs for Mul are not in the same graph!")

    # Description for python structures
    desc = 'ElemWise2Op'
    params = [elemwise_2op_dict['Div']]

    # Call deepRACIN
    onode = Node(lib.dR_ElemWise2Operation(input_node1.graph.ptr, input_node1.ptr, input_node2.ptr,
                                           elemwise_1op_dict['Div']), input_node1.graph, desc, params)
    return onode

def Pow(input_node1: Node, input_node2: Node):
    if input_node1.graph != input_node2.graph:
        sys.exit("DR Error: Inputs for Mul are not in the same graph!")

    # Description for python structures
    desc = 'ElemWise2Op'
    params = [elemwise_2op_dict['Pow']]

    # Call deepRACIN
    onode = Node(lib.dR_ElemWise2Operation(input_node1.graph.ptr, input_node1.ptr, input_node2.ptr,
                                           elemwise_1op_dict['Pow']), input_node1.graph, desc, params)
    return onode

def Softmax(input_node: Node):

    # Description for python structures
    desc = 'Softmax'
    params = [' ']

    # Call deepRACIN
    onode = Node(lib.dR_Softmax(input_node.graph.ptr, input_node.ptr),input_node.graph, desc, params)
    return onode

def Resolve_RoI(input_node: Node, shape: (int, int, int)):

    # Description for python structures
    desc = 'ResolveRoI'
    params = [shape[0], shape[1], shape[2]]

    # Call deepRACIN
    onode = Node(lib.dR_ResolveRoI(input_node.graph.ptr, input_node.ptr, Shape3(*shape)),input_node.graph, desc, params)
    return onode

def RGB_to_gray(input_node: Node):

    # Description for python structures
    desc = 'RGB2Gray'
    params = [' ']

    # Call deepRACIN
    onode = Node(lib.dR_RGB2gray(input_node.graph.ptr, input_node.ptr),input_node.graph, desc, params)
    return onode

def Upscaling(input_node: Node, upscaling_type: str, scale_factor_x: int, scale_factor_y: int):

    # Description for python structures
    desc = 'Upscaling'
    params = [us_dict[upscaling_type], scale_factor_x, scale_factor_y]

    # Call deepRACIN
    onode = Node(lib.dR_Upscaling(input_node.graph.ptr, input_node.ptr, us_dict[upscaling_type],
                                  scale_factor_x, scale_factor_y),input_node.graph, desc, params)
    return onode

def Create_Labels(input_node: Node, label_creation_type: str):

    # Description for python structures
    desc = 'LabelCreation'
    params = [lc_dict[label_creation_type]]

    # Call deepRACIN
    onode = Node(lib.dR_LabelCreation(input_node.graph.ptr, input_node.ptr, lc_dict[label_creation_type],
                                      0.0, 0.0, 0.0),input_node.graph, desc, params)
    return onode

def Normalization(input_node: Node, normalization_type : str, target_mean: float, target_dev: float):

    # Description for python structures
    desc = 'Normalization'
    params = [norm_dict[normalization_type], target_mean, target_dev]

    # Call deepRACIN
    onode = Node(lib.dR_Normalization(input_node.graph.ptr, input_node.ptr, norm_dict[normalization_type], target_mean,
                                      target_dev),input_node.graph, desc, params)
    return onode

def Pooling(input_node: Node, pooling_type: str, shape: (int, int, int, int), stride: (int, int, int, int)):

    # Description for python structures
    desc = 'Pooling'
    params = [pool_dict[pooling_type],shape[0],shape[1],shape[2],shape[3],stride[0],stride[1],stride[2],stride[3]]

    # Call deepRACIN
    onode = Node(lib.dR_Pooling(input_node.graph.ptr, input_node.ptr, Shape4(*shape), Shape4(*stride),
                                pool_dict[pooling_type]),input_node.graph, desc, params)
    return onode

def Slice(input_node: Node, origin: (int, int, int), shape: (int, int, int)):
    dr_shape = shape
    dr_origin = origin
    if input_node.graph.layout == 'WHC':
        dr_shape = [shape[0],shape[1],shape[2],0]
        dr_origin = [origin[0],origin[1],origin[2],0]
    elif input_node.graph.layout == 'CHW':
        dr_shape = [shape[2],shape[1],shape[0],0]
        dr_origin = [origin[2],origin[1],origin[0],0]
    elif input_node.graph.layout == 'HWC':
        dr_shape = [shape[1],shape[0],shape[2],0]
        dr_origin = [origin[1],origin[0],origin[2],0]

    # Description for python structures
    desc = 'Slice'
    params = [dr_origin[0],dr_origin[1],dr_origin[2],dr_origin[3],dr_shape[0],dr_shape[1],dr_shape[2],dr_shape[3]]

    # Call deepRACIN
    onode = Node(lib.dR_Slice(input_node.graph.ptr, input_node.ptr, Shape4(*dr_origin), Shape4(*dr_shape)),
                 input_node.graph, desc, params)
    return onode

def Crop_Or_Pad(input_node: Node, shape: (int, int, int)):
    dr_shape = shape
    if input_node.graph.layout == 'WHC':
        dr_shape = [shape[0],shape[1],shape[2],0]
    elif input_node.graph.layout == 'CHW':
        dr_shape = [shape[2],shape[1],shape[0],0]
    elif input_node.graph.layout == 'HWC':
        dr_shape = [shape[1],shape[0],shape[2],0]

    # Description for python structures
    desc = 'CropOrPad'
    params = [dr_shape[0],dr_shape[1],dr_shape[2]]

    # Call deepRACIN
    onode = Node(lib.dR_Slice(input_node.graph.ptr, input_node.ptr, Shape4(*dr_shape)),input_node.graph, desc, params)
    return onode


def Concat(input_nodes: list,  concat_dim: int, layout='HWC'):
    n = len(input_nodes)
    if not n > 1:
        sys.exit("DR Error: Concat with one or less nodes not allowed!")
    dr_dim = concat_dim
    graph = input_nodes[0].graph
    if graph.layout == 'WHC':
        dr_dim = [0, 1, 2][concat_dim]
    if graph.layout == 'CHW':
        dr_dim = [2, 1, 0][concat_dim]
    elif graph.layout == 'HWC':
        dr_dim = [1, 0, 2][concat_dim]

    nodeptr = (c_void_p * n)()
    for i in range(n):
        nodeptr[i] = input_nodes[i].ptr
        if input_nodes[i].graph != graph:
            sys.exit("DR Error: Inputs for Concat are not in the same graph!")

    # Description for python structures
    desc = 'Concat'
    params = [n,dr_dim]

    # Call deepRACIN
    onode = Node(lib.dR_Concat(graph.ptr, nodeptr, n, dr_dim),graph, desc, params)
    return onode



# Functions for using an existing OpenCL context and existing feed/output buffers. Not supported in python interface.
'''

void dR_setClEnvironment(dR_Graph* net,
                                cl_context clcontext,
                                cl_platform_id clplatformid,
                                cl_command_queue clcommandqueue,
                                cl_device_id cldeviceid);

gboolean dR_setDataFeedNodeBuffer(dR_Graph* graph, dR_Node* feednode, cl_mem* clbuf);


gboolean dR_setNodeRoIBufferAndIndex(dR_Node* node, cl_mem* buf, gint index);


gboolean dR_setPreexistingOutputBuffer(dR_Graph* graph, dR_Node* node, cl_mem* buf);


gboolean dR_setNodeRoI(dR_Node* node, dR_Shape3 origin);
'''