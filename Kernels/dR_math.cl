/**
* \brief Convertes RGB Image to Grayscale by averaging over depth
* \param[in] gInput Input Image
* \param[out] outputArr Output Image
* \author jan
*/
__kernel void RGB2Gray(
    const __global  float * gInput,
    __global float* outputArr
    )
{
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int width = get_global_size(0);
    int height = get_global_size(1);
    int gid = gy*width + gx;

    outputArr[gid] = (gInput[gid]+gInput[width*height+gid]+gInput[2*width*height+gid])/3;
}



/**
* \brief Adds to nodes element-wise
* \param[in] gInput1 Input Buffer 1
* \param[in] gInput2 Input Buffer 2
* \param[out] outputArr Output Image
* \author jan
*/
__kernel void elemWiseAdd(
    const __global  float * gInput1,
    const __global  float * gInput2,
    __global float* outputArr
    )
{
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int gz = (int) get_global_id(2);
    int gid = mad24(gz, (int)get_global_size(0)*(int)get_global_size(1), mad24(gy, (int)get_global_size(0), gx));
    outputArr[gid] = gInput1[gid]+gInput2[gid];
}

/**
* \brief Subtracts input 2 from input 1 element-wise
* \param[in] gInput1 Input Buffer 1
* \param[in] gInput2 Input Buffer 2
* \param[out] outputArr Output Image
* \author jan
*/
__kernel void elemWiseSub(
    const __global  float * gInput1,
    const __global  float * gInput2,
    __global float* outputArr
    )
{
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int gz = (int) get_global_id(2);
    int gid = mad24(gz, (int)get_global_size(0)*(int)get_global_size(1), mad24(gy, (int)get_global_size(0), gx));
    outputArr[gid] = gInput1[gid]-gInput2[gid];
}

/**
* \brief Multiplies to nodes element-wise
* \param[in] gInput1 Input Buffer 1
* \param[in] gInput2 Input Buffer 2
* \param[out] outputArr Output Image
* \author jan
*/
__kernel void elemWiseMul(
    const __global  float * gInput1,
    const __global  float * gInput2,
    __global float* outputArr
    )
{
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int gz = (int) get_global_id(2);
    int gid = mad24(gz, (int)get_global_size(0)*(int)get_global_size(1), mad24(gy, (int)get_global_size(0), gx));
    outputArr[gid] = gInput1[gid]*gInput2[gid];
}

/**
* \brief Divides input1 through input2 element-wise
* \param[in] gInput1 Input Buffer 1
* \param[in] gInput2 Input Buffer 2
* \param[out] outputArr Output Image
* \author jan
*/
__kernel void elemWiseDiv(
    const __global  float * gInput1,
    const __global  float * gInput2,
    __global float* outputArr
    )
{
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int gz = (int) get_global_id(2);
    int gid = mad24(gz, (int)get_global_size(0)*(int)get_global_size(1), mad24(gy, (int)get_global_size(0), gx));
    outputArr[gid] = gInput1[gid]/gInput2[gid];
}

/**
* \brief Computes input1^input2 element-wise
* \param[in] gInput1 Input Buffer 1
* \param[in] gInput2 Input Buffer 2
* \param[out] outputArr Output Image
* \author jan
*/
__kernel void elemWisePow(
    const __global  float * gInput1,
    const __global  float * gInput2,
    __global float* outputArr
    )
{
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int gz = (int) get_global_id(2);
    int gid = mad24(gz, (int)get_global_size(0)*(int)get_global_size(1), mad24(gy, (int)get_global_size(0), gx));
    outputArr[gid] = pow(gInput1[gid],gInput2[gid]);
}


/**
* \brief Computes (Element+scalaradd)*scalarmul for every image element
* \param[in] gInput Input Image
* \param[out] outputArr Output Image
* \param[in] scalaradd scalar value
* \param[in] scalarmul scalar value
* \author jan
*/
__kernel void addMulScalar(
    const __global  float * gInput,
    __global float* outputArr,
    float scalaradd,
    float scalarmul
    )
{
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int gz = (int) get_global_id(2);
    int gid = mad24(gz, (int)get_global_size(0)*(int)get_global_size(1), mad24(gy, (int)get_global_size(0), gx));
    outputArr[gid] = (gInput[gid]+scalaradd)*scalarmul;
}


/**
* \brief Computes Element*scalarmul+scalaradd for every image element
* \param[in] gInput Input Image
* \param[out] outputArr Output Image
* \param[in] scalarmul scalar value
* \param[in] scalaradd scalar value
* \author jan
*/
__kernel void madScalar(
    const __global  float * gInput,
    __global float* outputArr,
    float scalarmul,
    float scalaradd
    )
{
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int gz = (int) get_global_id(2);
    int gid = mad24(gz, (int)get_global_size(0)*(int)get_global_size(1), mad24(gy, (int)get_global_size(0), gx));
    outputArr[gid] = gInput[gid]*scalarmul+scalaradd;
}

/**
* \brief Adds scalar value to every image element
* \param[in] gInput Input Image
* \param[out] outputArr Output Image
* \param[in] scalar scalar value
* \author jan
*/
__kernel void addScalar(
    const __global  float * gInput,
    __global float* outputArr,
    float scalar
    )
{
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int gz = (int) get_global_id(2);
    int gid = mad24(gz, (int)get_global_size(0)*(int)get_global_size(1), mad24(gy, (int)get_global_size(0), gx));
    outputArr[gid] = gInput[gid]+scalar;
}

/**
* \brief Subtracts scalar value from every buffer element
* \param[in] gInput Input Image
* \param[out] outputArr Output Image
* \param[in] scalar scalar value
* \author jan
*/
__kernel void subScalar(
    const __global  float * gInput,
    __global float* outputArr,
    float scalar
    )
{
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int gz = (int) get_global_id(2);
    int gid = mad24(gz, (int)get_global_size(0)*(int)get_global_size(1), mad24(gy, (int)get_global_size(0), gx));
    outputArr[gid] = gInput[gid]-scalar;
}

/**
* \brief Multiplies every element of buffer by a scalar value
* \param[in] gInput Input Image
* \param[out] outputArr Output Image
* \param[in] scalar scalar value
* \author jan
*/
__kernel void mulScalar(
    __global  float * gInput,
    __global float* outputArr,
    float scalar
    )
{
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int gz = (int) get_global_id(2);
    int gid = mad24(gz, (int)get_global_size(0)*(int)get_global_size(1), mad24(gy, (int)get_global_size(0), gx));
    outputArr[gid] = gInput[gid]*scalar;
}

/**
* \brief Divides every element from image through scalar value
* \param[in] gInput Input Image
* \param[out] outputArr Output Image
* \param[in] scalar scalar value
* \author jan
*/
__kernel void divScalar(
    __global  float * gInput,
    __global float* outputArr,
    float scalar
    )
{
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int gz = (int) get_global_id(2);
    int gid = mad24(gz, (int)get_global_size(0)*(int)get_global_size(1), mad24(gy, (int)get_global_size(0), gx));
    outputArr[gid] = gInput[gid]/scalar;
}

/**
* \brief Computes x^scalar for each element x in input
* \param[in] gInput Input Image
* \param[out] outputArr Output Image
* \param[in] scalar scalar value
* \author jan
*/
__kernel void powScalar(
    __global  float * gInput,
    __global float* outputArr,
    float scalar
    )
{
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int gz = (int) get_global_id(2);
    int gid = mad24(gz, (int)get_global_size(0)*(int)get_global_size(1), mad24(gy, (int)get_global_size(0), gx));
    outputArr[gid] = pow(gInput[gid],scalar);
}

/**
* \brief Computs log(x) (natural) for every image element
* \param[in] gInput Input Image
* \param[out] outputArr Output Image
* \param[in] scalar scalar value
* \author jan
*/
__kernel void computeLog(
    const __global  float * gInput,
    __global float* outputArr
    )
{
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int gz = (int) get_global_id(2);
    int gid = mad24(gz, (int)get_global_size(0)*(int)get_global_size(1), mad24(gy, (int)get_global_size(0), gx));
    outputArr[gid] = log(gInput[gid]);
}


/**
* \brief Computes e^x for every element of input image
* \param[in] gInput Input Image
* \param[out] outputArr Output Image
* \author jan
*/
__kernel void computeExp(
    __global float* gInput,
    __global float* outputArr
    )
{
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int gz = (int) get_global_id(2);
    int gid = mad24(gz, (int)get_global_size(0)*(int)get_global_size(1), mad24(gy, (int)get_global_size(0), gx));
    outputArr[gid] = exp(gInput[gid]);
}

/**
* \brief Computes sqrt(x) for every element of input buffer
* \param[in] gInput Input Image
* \param[out] outputArr Output Image
* \author jan
*/
__kernel void computeSqrt(
    __global float* gInput,
    __global float* outputArr
    )
{
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int gz = (int) get_global_id(2);
    int gid = mad24(gz, (int)get_global_size(0)*(int)get_global_size(1), mad24(gy, (int)get_global_size(0), gx));
    outputArr[gid] = sqrt(gInput[gid]);
}

/**
* \brief Fills buffer with constant
* \param[in] gInput Input Image
* \param[out] outputArr Output Image
* \author jan
*/
__kernel void fill(
    __global float* gInput,
    __global float* outputArr,
    float scalar
    )
{
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int gz = (int) get_global_id(2);
    int gid = mad24(gz, (int)get_global_size(0)*(int)get_global_size(1), mad24(gy, (int)get_global_size(0), gx));
    outputArr[gid] = scalar;
}

/* --------------FFT for RGB: Out of place-------------- */

/* complex numbers definitions https://stackoverflow.com/questions/10016125/complex-number-support-in-opencl */
#ifndef M_PI
#define M_PI 3.1416
#endif
/* Return Real (Imaginary) component of complex number */
inline float real(float2 a){
     return a.x;
}
inline float imag(float2 a){
     return a.y;
}

/* Complex multiplication */
#define MUL(a, b, tmp) { tmp = a; a.x = tmp.x*b.x - tmp.y*b.y; a.y = tmp.x*b.y + tmp.y*b.x; }

/* Butterfly operation */
#define DFT2( a, b, tmp) { tmp = a - b; a += b; b = tmp; }

/* Return cos(alpha)+I*sin(alpha) */
float2 exp_alpha(float alpha)
{
  float cs,sn;
  sn = sincos(alpha,&cs);
  return (float2)(cs,sn);
}

/* Dimensions of input */
/*
#define X 4
#define Y 4
#define Z 3 // 3 for RGB
*/
//static const unsigned char BitReverseTable[4] = { 0x0, 0x2, 0x1, 0x3 };
/* Input size N, for 1D FFT N/2 threads, each thread doing one DFT2
 * Input size X*Y*Z, for Z times 2D FFT, Z = 3 for RGB
 * Output size X*Y*6
 * 1) rows: Y*(X/2)*Z work items at once
 * 2) columns: X*(Y/2)*Z work items at once
 */
/*********************************** RGB FFT ******************************************/
#if 0
 void fft_rows(
     __global float * in,
     __global float * out,
     int gid,
     int offset,
     int imag_offset,
     int width,
     int p
   )
 {
   int k = (gid - offset) & (p-1); // index in input sequence, in 0..P-1

   float2 u0;
   float2 u1;
   if (p == 1) // only real input
   {
     u0.x = in[gid];
     u0.y = 0;

     u1.x = in[gid + (width/2)];
     u1.y = 0;
   }
   else // get real and imaginary part
   {
     u0.x = in[gid]; //real part
     u0.y = in[gid+imag_offset]; //imag part

     u1.x = in[gid + (width/2)];
     u1.y = in[gid + (width/2) + imag_offset];
   }


   float2 twiddle = exp_alpha( (float)k*(-1)*M_PI / (float)p ); // p in denominator, k
   float2 tmp;

   MUL(u1,twiddle,tmp);

   DFT2(u0,u1,tmp);

   int j = ((gid - offset) <<1) - k; // = ((i-k)<<1)+k
   j += offset;

   out[j] = real(u0);
   out[j+p] = real(u1);

   out[j+imag_offset] = imag(u0);
   out[j+p+imag_offset] = imag(u1);
 }

 void fft_columns(
     __global float * in,
     __global float * out,
     int gid,
     int offset,
     int imag_offset,
     int width,
     int p,
     int offset_xy,
     int gz,
     int height,
     int gx
   )
   {
     int offset_in_xy_1 = gid - offset_xy * gz;
     int in_1Dx = offset_xy / width;

     int k = in_1Dx & (p-1); // index in input sequence, in 0..P-1

     float2 u0;
     float2 u1;
     u0.x = in[gid]; //real part
     u0.y = in[gid+imag_offset]; //imag part

     u1.x = in[gid + (height/2)*width];
     u1.y = in[gid + (height/2)*width + imag_offset];

     float2 twiddle = exp_alpha( (float)k*(-1)*M_PI / (float)p ); // p in denominator, k
     float2 tmp;

     MUL(u1,twiddle,tmp);

     DFT2(u0,u1,tmp);

     int j = (in_1Dx << 1) - k; // = ((i-k)<<1)+k
     j *= width;
     j += offset_xy*gz;
     j += gx;

     out[j] = real(u0);
     out[j+p] = real(u1);

     out[j+imag_offset] = imag(u0);
     out[j+p+imag_offset] = imag(u1);
   }

__kernel void fft_rgb(
    const __global float * gInput,
    __global float * intermedBuf,
    __global float * outputArr
    )
{
    /* For RGB do */
    /*  Bit reverse rows  */
    /*  FFT on rows */
    /*  Bit reverse columns */
    /*  FFT on columns */

    /* Each work item has a three dimensional identifier */
    int gx = (int) get_global_id(0);
    int gy = (int) get_global_id(1);
    int gz = (int) get_global_id(2);
    int width = (int) get_global_size(0);
    int height = (int) get_global_size(1);
    int depth = (int) get_global_size(2);
    int gid = height*(width/2)*gz + (width/2)*gy + gx;
    /* offset for scaling down (and up) of indices to 1D FFT indices */
    int offset = gid - (width/2)*height*gz - (width/2)*gy;
    int offset_xy = width*(height/2);
    int imag_offset = width*height*3;

    int even_odd = 0;
    /* FFT for rows */
    /* insert barrier between loop invocations */
    for(int p = 1; p <= width; p *= 2)
    {
      if (p == 1)
      {
        fft_rows(gInput, outputArr, gid, offset, imag_offset, width, p);
      }
      else
      {
        if (even_odd % 2) // odd
        {
          fft_rows(outputArr, intermedBuf, gid, offset, imag_offset, width, p);
        }
        else // even
        {
          fft_rows(intermedBuf, outputArr, gid, offset, imag_offset, width, p);
        }
      }
      even_odd++;
    }
    /* insert barrier */
    /* TODO: store info about whether rows FFT ended on outputArr or intermedBuf */
    int even_odd2 = 0;
    for(int p = 1; p <= width; p *= 2)
    {
      if (even_odd2 % 2) // odd
      {
        fft_columns(outputArr, intermedBuf, gid, offset, imag_offset, width, p, offset_xy, gz, height, gx);
      }
      else // even
      {
        fft_columns(intermedBuf, outputArr, gid, offset, imag_offset, width, p, offset_xy, gz, height, gx);
      }
      even_odd2++;
    }
    /* collumns need different work items if image not quadratic in X and Y */
}
#endif
/******************** 1D test fft: only transform first row of image*********************/
#if 0
//TODO: Inverse test successful, only works till 64*64 images. 128*128 and 256*256 give wrong results
void one_dim(
  __global float * in,
  __global float * out,
  int p,
  int i,
  int w,
  int imag_offset,
  int inverse
)
{
  int k = (i) & (p-1); // index in input sequence, in 0..P-1

  float2 u0;
  float2 u1;

  if (p == 1 && (inverse == 0)) // only real input
  {
    u0.x = in[i];
    u0.y = 0;

    u1.x = in[i + (w/2)];
    u1.y = 0;
  }
  else // get real and imaginary part
  {
    u0.x = in[i]; //real part
    u0.y = in[i+imag_offset]; //imag part

    u1.x = in[i + (w/2)];
    u1.y = in[i + (w/2) + imag_offset];
  }

  float2 twiddle;
  float2 tmp;

  if (inverse)
  {
     twiddle = exp_alpha( (float)(k)*M_PI / (float)(p) ); // p in denominator, k
  }
  else
  {
     twiddle = exp_alpha( (float)(k)*(-1)*M_PI / (float)(p) ); // p in denominator, k
  }

  MUL(u1,twiddle,tmp);

  DFT2(u0,u1,tmp);

  int j = ((i) << 1) - k;

  out[j] = real(u0);
  out[j+p] = real(u1);

  out[j+imag_offset] = imag(u0);
  out[j+p+imag_offset] = imag(u1);
}

__kernel void fft_one_dim(
  const __global float * gInput,
  __global float * intermedBuf,
  __global float * outputArr
)
{
  int i = get_global_id(0);
  int w = (int) get_global_size(0);
  int h = (int) get_global_size(1);
  int imag_offset = w*h;

  int even_odd = 0;
  int lastIn = 0;

  barrier(CLK_GLOBAL_MEM_FENCE);
  intermedBuf[i] = 0.0;
  outputArr[i] = 0.0;
  barrier(CLK_GLOBAL_MEM_FENCE);

  if ( i < w/2 )// only first and second element
  {
    for(int p = 1; p <= w/2; p *= 2)
    {
      if (p==1)
      {
        one_dim(gInput, outputArr, p, i, w, imag_offset, 0);
      }
      else
      {
        if (even_odd % 2) // odd
        {
          one_dim(outputArr, intermedBuf, p, i, w, imag_offset, 0);
          lastIn = 0;
        }
        else // even
        {
          one_dim(intermedBuf, outputArr, p, i, w, imag_offset, 0);
          lastIn = 1;
        }
      }
      even_odd++;
      barrier(CLK_GLOBAL_MEM_FENCE);
    }

    barrier(CLK_GLOBAL_MEM_FENCE);
    if( lastIn == 0 )
    {
      outputArr[i] = intermedBuf[i];
      outputArr[i + w/2] = intermedBuf[i + w/2];
      outputArr[i + imag_offset] = intermedBuf[i + imag_offset];
      outputArr[i + w/2 + imag_offset] = intermedBuf[i + w/2 + imag_offset];
    }

    barrier(CLK_GLOBAL_MEM_FENCE);
    //when doing inverse, begin with odd call, so =1
    int even_odd = 1;
    int lastIn = 1;
    barrier(CLK_GLOBAL_MEM_FENCE);

    #if 1

    /* Do inverse 1D FFT */
    for(int p = 1; p <= w/2; p *= 2)
    {
      if (even_odd % 2) // odd
      {
        one_dim(outputArr, intermedBuf, p, i, w, imag_offset, 1);
        lastIn = 0;
      }
      else // even
      {
        one_dim(intermedBuf, outputArr, p, i, w, imag_offset, 1);
        lastIn = 1;
      }
      even_odd++;
      barrier(CLK_GLOBAL_MEM_FENCE);
    }

    barrier(CLK_GLOBAL_MEM_FENCE);
    if( lastIn == 0 )
    {
      outputArr[i] = intermedBuf[i];
      outputArr[i + w/2] = intermedBuf[i + w/2];
      outputArr[i + imag_offset] = intermedBuf[i + imag_offset];
      outputArr[i + w/2 + imag_offset] = intermedBuf[i + w/2 + imag_offset];
    }
    #endif
  }
  barrier(CLK_GLOBAL_MEM_FENCE);
  outputArr[i] /= w;
}

#endif
/******************** 2D only rows grayscale test fft *********************/
// TODO: tested with inverse, works up to 256*256. for bigger images something with barriers may need to be fixed.
#if 1
void two_dim_rows(
  __global float * in,
  __global float * out,
  int p,
  int gid,
  int gx,
  int gy,
  int w,
  int imag_offset,
  int offset,
  int inverse
)
{
  if( (gx) < w/2 ) // TODO: replace gid-offset with gx
  {
    int k = (gx) & (p-1);

    float2 u0;
    float2 u1;

    if (p == 1 && (inverse == 0)) // only real input
    {
      u0.x = in[gid];
      u0.y = 0;

      u1.x = in[gid + (w/2)];
      u1.y = 0;
    }
    else // get real and imaginary part
    {
      u0.x = in[gid]; //real part
      u0.y = in[gid+imag_offset]; //imag part

      u1.x = in[gid + (w/2)];
      u1.y = in[gid + (w/2) + imag_offset];
    }

    float2 twiddle;
    float2 tmp;

    if (inverse)
    {
       twiddle = exp_alpha( (float)(k)*M_PI / (float)(p) ); // p in denominator, k
    }
    else
    {
       twiddle = exp_alpha( (float)(k)*(-1)*M_PI / (float)(p) ); // p in denominator, k
    }

    MUL(u1,twiddle,tmp);

    DFT2(u0,u1,tmp);

    int j = ((gx) << 1) - k;
    j += offset;

    out[j] = real(u0);
    out[j+p] = real(u1);

    out[j+imag_offset] = imag(u0);
    out[j+p+imag_offset] = imag(u1);
  }
}
/* Kernel function */
__kernel void fft(
  const __global float * gInput,
  __global float * intermedBuf,
  __global float * outputArr
)
{
  int gx = get_global_id(0);
  int gy = get_global_id(1);
  int w = (int) get_global_size(0);
  int h = (int) get_global_size(1);
  int gid = w*gy + gx;
  int imag_offset = w*h;
  int offset = gy*w;

  int even_odd = 0;
  int lastIn = 0;

  barrier(CLK_GLOBAL_MEM_FENCE);
  // TODO: not needed, maybe do somewhere else
  intermedBuf[gid] = 0.0;
  outputArr[gid] = 0.0;
  outputArr[gid + imag_offset] = 0.0;
  barrier(CLK_GLOBAL_MEM_FENCE);

  for(int p = 1; p <= w/2; p *= 2)
  {
    if (p==1)
    {
      two_dim_rows(gInput, outputArr, p, gid, gx, gy, w, imag_offset, offset, 0);
    }
    else
    {
      if (even_odd % 2) // odd
      {
        two_dim_rows(outputArr, intermedBuf, p, gid, gx, gy, w, imag_offset, offset, 0);
        lastIn = 0;
      }
      else // even
      {
        two_dim_rows(intermedBuf, outputArr, p, gid, gx, gy, w, imag_offset, offset, 0);
        lastIn = 1;
      }
    }
    even_odd++;
    barrier(CLK_GLOBAL_MEM_FENCE);
  }

  barrier(CLK_GLOBAL_MEM_FENCE);
  if( lastIn == 0 )
  {
    // TODO: just change pointer instead of copy
    outputArr[gid] = intermedBuf[gid];
    outputArr[gid + imag_offset] = intermedBuf[gid + imag_offset];
  }

  barrier(CLK_GLOBAL_MEM_FENCE);
  //next, begin with odd call, so even_odd=1
  even_odd = 1;
  lastIn = 1;

  // transpose, TODO: use more efficient transpose
  barrier(CLK_GLOBAL_MEM_FENCE);
  intermedBuf[gx*w + gy] = outputArr[gid];
  intermedBuf[gx*w + gy + imag_offset] = outputArr[gid + imag_offset];
  barrier(CLK_GLOBAL_MEM_FENCE);
  // TODO: just change pointer instead of copy
  outputArr[gid] = intermedBuf[gid];
  outputArr[gid + imag_offset] = intermedBuf[gid + imag_offset];

  barrier(CLK_GLOBAL_MEM_FENCE);
  // after transpose, do fft on rows again.
  for(int p = 1; p <= w/2; p *= 2)
  {
    if (even_odd % 2) // odd
    {
      two_dim_rows(outputArr, intermedBuf, p, gid, gx, gy, w, imag_offset, offset, 1);
      lastIn = 0;
    }
    else // even
    {
      two_dim_rows(intermedBuf, outputArr, p, gid, gx, gy, w, imag_offset, offset, 1);
      lastIn = 1;
    }
    even_odd++;
    barrier(CLK_GLOBAL_MEM_FENCE);
  }

  barrier(CLK_GLOBAL_MEM_FENCE);
  if( lastIn == 0 )
  {
    outputArr[gid] = intermedBuf[gid];
    outputArr[gid + imag_offset] = intermedBuf[gid + imag_offset];
  }

  // transpose again.
  barrier(CLK_GLOBAL_MEM_FENCE);
  intermedBuf[gx*w + gy] = outputArr[gid];
  intermedBuf[gx*w + gy + imag_offset] = outputArr[gid + imag_offset];
  barrier(CLK_GLOBAL_MEM_FENCE);
  // TODO: just change pointer instead of copy
  outputArr[gid] = intermedBuf[gid];
  outputArr[gid + imag_offset] = intermedBuf[gid + imag_offset];

  #if 0

  /* Do inverse 1D FFT */
  for(int p = 1; p <= w/2; p *= 2)
  {
    if (even_odd % 2) // odd
    {
      two_dim_rows(outputArr, intermedBuf, p, gid, gx, gy, w, imag_offset, offset, 1);
      lastIn = 0;
    }
    else // even
    {
      two_dim_rows(intermedBuf, outputArr, p, gid, gx, gy, w, imag_offset, offset, 1);
      lastIn = 1;
    }
    even_odd++;
    barrier(CLK_GLOBAL_MEM_FENCE);
  }

  barrier(CLK_GLOBAL_MEM_FENCE);
  if( lastIn == 0 )
  {
    outputArr[gid] = intermedBuf[gid];
    outputArr[gid + imag_offset] = intermedBuf[gid + imag_offset];
  }
  barrier(CLK_GLOBAL_MEM_FENCE);
  outputArr[gid] /= w;
  #endif
}

#endif
/******************** 2D only columns grayscale test fft *********************/
#if 0
void two_dim_columns(
  __global float * in,
  __global float * out,
  int p,
  int gid,
  int gx,
  int gy,
  int w,
  int h,
  int imag_offset,
  int offset,
  int inverse
)
{
  if( gy < h/2 )
  {
    int k = (gy) & (p-1);

    float2 u0;
    float2 u1;

    if (p == 1 && (inverse == 0)) // only real input
    {
      u0.x = in[gid];
      u0.y = 0;

      u1.x = in[gid + w*(h/2)];
      u1.y = 0;
    }
    else // get real and imaginary part
    {
      u0.x = in[gid]; //real part
      u0.y = in[gid+imag_offset]; //imag part

      u1.x = in[gid + w*(h/2)];
      u1.y = in[gid + w*(h/2) + imag_offset];
    }

    float2 twiddle;
    float2 tmp;

    if (inverse)
    {
       twiddle = exp_alpha( (float)(k)*M_PI / (float)(p) ); // p in denominator, k
    }
    else
    {
       twiddle = exp_alpha( (float)(k)*(-1)*M_PI / (float)(p) ); // p in denominator, k
    }

    MUL(u1,twiddle,tmp);

    DFT2(u0,u1,tmp);

    int j = ((gy) << 1) - k;
    j *= w;
    j += gx;

    out[j] = real(u0);
    out[j+w*p] = real(u1);

    out[j+imag_offset] = imag(u0);
    out[j+w*p+imag_offset] = imag(u1);
  }
  // TODO: losing half the workitems here ?
}
/* Kernel function */
__kernel void fft(
  const __global float * gInput,
  __global float * intermedBuf,
  __global float * outputArr
)
{
  int gx = get_global_id(0);
  int gy = get_global_id(1);
  int w = (int) get_global_size(0);
  int h = (int) get_global_size(1);
  int gid = w*gy + gx;
  int imag_offset = w*h;
  int offset = gy*w;

  int even_odd = 0;
  int lastIn = 0;

  barrier(CLK_GLOBAL_MEM_FENCE);
  intermedBuf[gid] = 0.0;
  outputArr[gid] = 0.0;
  outputArr[gid + imag_offset] = 0.0;
  barrier(CLK_GLOBAL_MEM_FENCE);

  for(int p = 1; p <= h/2; p *= 2)
  {
    if (p==1)
    {
      two_dim_columns(gInput, outputArr, p, gid, gx, gy, w, h, imag_offset, offset, 0);
    }
    else
    {
      if (even_odd % 2) // odd
      {
        two_dim_columns(outputArr, intermedBuf, p, gid, gx, gy, w, h, imag_offset, offset, 0);
        lastIn = 0;
      }
      else // even
      {
        two_dim_columns(intermedBuf, outputArr, p, gid, gx, gy, w, h, imag_offset, offset, 0);
        lastIn = 1;
      }
    }
    even_odd++;
    barrier(CLK_GLOBAL_MEM_FENCE);
  }
  // why are just w*h/2 work items left? where is the other half?
  barrier(CLK_GLOBAL_MEM_FENCE);
  if( lastIn == 0 )
  {
    outputArr[gid] = intermedBuf[gid];
    outputArr[gid + imag_offset] = intermedBuf[gid + imag_offset];
  }

  barrier(CLK_GLOBAL_MEM_FENCE);
  //when doing inverse, begin with odd call, so =1
  even_odd = 1;
  lastIn = 1;
  barrier(CLK_GLOBAL_MEM_FENCE);

  #if 1

  /* Do inverse 1D FFT */
  for(int p = 1; p <= h/2; p *= 2)
  {
    if (even_odd % 2) // odd
    {
      two_dim_columns(outputArr, intermedBuf, p, gid, gx, gy, w, h, imag_offset, offset, 1);
      lastIn = 0;
    }
    else // even
    {
      two_dim_columns(intermedBuf, outputArr, p, gid, gx, gy, w, h, imag_offset, offset, 1);
      lastIn = 1;
    }
    even_odd++;
    barrier(CLK_GLOBAL_MEM_FENCE);
  }

  barrier(CLK_GLOBAL_MEM_FENCE);
  if( lastIn == 0 )
  {
    outputArr[gid] = intermedBuf[gid];
    outputArr[gid + imag_offset] = intermedBuf[gid + imag_offset];
  }
  barrier(CLK_GLOBAL_MEM_FENCE);
  outputArr[gid] /= h;
  #endif

}

#endif
