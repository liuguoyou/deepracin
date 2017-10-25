#include "dR_nodes_fft.h"
#include "dR_core.h"

// ///////////////////////////
// Fast Fourier Transform //
// ///////////////////////////

dR_Node* dR_FFT(dR_Graph* net, dR_Node* inputNode1)
{
    dR_FFT_Data* fft = g_malloc(sizeof(dR_FFT_Data));
    dR_Node* l = g_malloc(sizeof(dR_Node));

    l->layer = fft;
    l->type = tFFT;

    l->compute = dR_fft_compute;
    l->schedule = dR_fft_schedule;
    l->propagateShape = dR_fft_propagateShape;
    l->getRequiredOutputBufferSize = dR_fft_getRequiredOutputBufferSize;
    l->createKernel = dR_fft_createKernel;
    l->allocateBuffers = dR_fft_allocateBuffers;
    l->fillBuffers = dR_fft_fillBuffers;
    l->cleanupBuffers = dR_fft_cleanupBuffers;
    l->cleanupLayer = dR_fft_cleanupLayer;
    l->serializeNode = dR_fft_serializeNode;
    l->parseAppendNode = dR_fft_parseAppendNode;
    l->printLayer = dR_fft_printLayer;

    l->generateKernel = NULL;
    l->createKernelName = NULL;
    l->setVariables = NULL;
    dR_appendLayer(net, l);
    return l;
}

gchar* dR_fft_serializeNode(dR_Node* layer, gchar* params[], gint* numParams, gfloat* variables[], gint variableSizes[], gint* numVariables)
{
    dR_FFT_Data* fft = (dR_FFT_Data*)(layer->layer);
    gchar* desc = "fft";
    gint numNodeParams = 1;
    gint numNodeVariables = 0;
    if(*numParams<numNodeParams||*numVariables<numNodeVariables)
    {
        g_print("SerializeNode needs space for %d parameters and %d variables!\n",numNodeParams,numNodeVariables);
        return NULL;
    }
    *numParams = numNodeParams;
    //params[0] = g_strdup_printf("%d",fft->op);

    *numVariables = numNodeVariables;
    return desc;
}

dR_Node* dR_fft_parseAppendNode(dR_Graph* net, dR_Node** iNodes, gint numINodes, gchar** params, gint numParams, gfloat** variables, gint numVariables)
{
    gint numNodeInputs = 2;
    gint numNodeParams = 1;
    gint numNodeVariables = 0;
    dR_Node* out;
    if(numINodes!=1)
    {
        g_print("Parsing Error: fft Node needs %d InputNodes but got %d!\n",numNodeInputs,numNodeVariables);
        return NULL;
    }
    if(numParams!=numNodeParams||numVariables!=numNodeVariables)
    {
        g_print("Parsing Error: fft Node needs %d Parameters and %d Variables!\n",numNodeParams,numNodeVariables);
        return NULL;
    }
    out = dR_FFT(net, iNodes[0]);
    return out;
}

gboolean dR_fft_schedule(dR_Graph* net, dR_Node* layer){
    // Nothing to do
    // Warnings shut up, please
    net = net;
    layer = layer;
    return TRUE;
 }


gboolean dR_fft_compute(dR_Graph* net, dR_Node* layer){
    size_t globalWorkSize[3];
    int paramid = 0;
    cl_mem* input1, *input2;
    dR_list_resetIt(layer->previous_layers);
    input1 = ((dR_Node*)dR_list_next(layer->previous_layers))->outputBuf->bufptr;
    input2 = ((dR_Node*)dR_list_next(layer->previous_layers))->outputBuf->bufptr;
    globalWorkSize[0] = layer->oshape.s0;
    globalWorkSize[1] = layer->oshape.s1;
    globalWorkSize[2] = layer->oshape.s2;


    net->clConfig->clError = clSetKernelArg(layer->clKernel, paramid, sizeof(cl_mem), (void *)input1);                      paramid++;
    net->clConfig->clError = clSetKernelArg(layer->clKernel, paramid, sizeof(cl_mem), (void *)input2);                      paramid++;
    net->clConfig->clError |= clSetKernelArg(layer->clKernel, paramid, sizeof(cl_mem), (void *)layer->outputBuf->bufptr);          paramid++;

    if (dR_openCLError(net, "Setting kernel args failed.", "Element-wise 2-operation Kernel"))
        return FALSE;
    // execute kernel
     net->clConfig->clError = clEnqueueNDRangeKernel(net->clConfig->clCommandQueue, layer->clKernel, 3, NULL, globalWorkSize,
        NULL, 0, NULL, net->clConfig->clEvent);

    return dR_finishCLKernel(net, "deepRACIN:fft");

}

gboolean dR_fft_propagateShape(dR_Graph* net, dR_Node* layer)
{
    dR_FFT_Data* fft = (dR_FFT_Data*)(layer->layer);
    dR_Node* lastlayer;
    if(layer->previous_layers->length!=2)
    {
        if(!net->config->silent)
            g_print("Elem-wise 2-operation Node with id %d has %d inputs but needs 2!\n",layer->layerID,layer->previous_layers->length);
        return FALSE;
    }
    dR_list_resetIt(layer->previous_layers);
    lastlayer = dR_list_next(layer->previous_layers);
    fft->ishape.s0 = lastlayer->oshape.s0;
    fft->ishape.s1 = lastlayer->oshape.s1;
    fft->ishape.s2 = lastlayer->oshape.s2;

    lastlayer = dR_list_next(layer->previous_layers);
    if(fft->ishape.s0!=lastlayer->oshape.s0||fft->ishape.s1!=lastlayer->oshape.s1||fft->ishape.s2!=lastlayer->oshape.s2)
    {
        if(!net->config->silent)
        {
            g_print("Elem-wise 2-operation Node needs 2 input nodes with the same shape!\n");
            g_print("[%d, %d, %d] and [%d, %d, %d] not matching!\n",
                    fft->ishape.s0,fft->ishape.s1,fft->ishape.s2,lastlayer->oshape.s0,lastlayer->oshape.s1,lastlayer->oshape.s2);
        }
        return FALSE;
    }
    layer->oshape.s0 = fft->ishape.s0;
    layer->oshape.s1 = fft->ishape.s1;
    layer->oshape.s2 = fft->ishape.s2;
    return TRUE;
}

gint32 dR_fft_getRequiredOutputBufferSize(dR_Node* layer)
{
    return layer->oshape.s0*layer->oshape.s1*layer->oshape.s2;
}

gboolean dR_fft_createKernel(dR_Graph* net, dR_Node* layer)
{
    dR_FFT_Data* fft = (dR_FFT_Data*)(layer->layer);
    gboolean ret=FALSE;
    /*
    switch(fft->op){
    case tAdd:
        ret = dR_createKernel(net,"elemWiseAdd",&(layer->clKernel));
        break;
    case tSub:
        ret = dR_createKernel(net,"elemWiseSub",&(layer->clKernel));
        break;
    case tMul:
        ret = dR_createKernel(net,"elemWiseMul",&(layer->clKernel));
        break;
    case tDiv:
        ret = dR_createKernel(net,"elemWiseDiv",&(layer->clKernel));
        break;
    case tPow:
        ret = dR_createKernel(net,"elemWisePow",&(layer->clKernel));
        break;
    }
    */
    return ret;
}


gboolean dR_fft_allocateBuffers(dR_Graph* net, dR_Node* layer)
{
    // Nothing to do
    // Warnings shut up, please
    net = net;
    layer = layer;
    return TRUE;
}

gboolean dR_fft_fillBuffers(dR_Graph* net, dR_Node* layer)
{
    // Nothing to do
    // Warnings shut up, please
    net = net;
    layer = layer;
    return TRUE;
}

gboolean dR_fft_cleanupBuffers(dR_Graph* net, dR_Node* layer)
{
    gboolean ret = TRUE;
    if(net->prepared)
        ret &= dR_cleanupKernel((layer->clKernel));
    return ret;
}

gboolean dR_fft_cleanupLayer(dR_Graph* net, dR_Node* layer)
{
    if(net->prepared)
        g_free((dR_FFT_Data*)(layer->layer));
    return TRUE;
}


gchar* dR_fft_printLayer(dR_Node* layer)
{
    dR_FFT_Data* fft = (dR_FFT_Data*)(layer->layer);
    gchar* out;
    gchar* op;
    /*
    switch(fft->op){
    case tAdd:
        op = "Add";
        break;
    case tSub:
        op = "Sub";
        break;
    case tMul:
        op = "Mul";
        break;
    case tDiv:
        op = "Div";
        break;
    case tPow:
        op = "Pow";
        break;
    default:
        op = "Error";
    }
    out = g_strdup_printf("%s%d%s%s%s",
            "Element-wise 2 input operation node: ",layer->layerID,
            "\n Operation: ", op,"\n");
    */
    return out;
}