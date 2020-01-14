#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "TutorialConfig.h"

#ifdef USE_MYMATH
#include "mysqrt.h"
#endif

int main(int argc, char *argv[])
{
    if(argc < 2)
    {
        fprintf(stdout, "%s Version %d.%d\n",
        argv[0],
        Tutorial_VERSION_MAJOR,
        Tutorial_VERSION_MINOR);
        fprintf(stdout, "Usage: %s number\n", argv[0]);
        return 1;
    }

    double inputvalue = atof(argv[1]);
    #if defined(HAVE_LOG) && defined(HAVE_EXP)
        double outputvalue = exp(log(inputvalue)*0.5);
    #else
        #ifdef USE_MYMATH
            double outputvalue = InvSqrt(inputvalue);
        #else
            double outputvalue = sqrt(inputvalue);
        #endif
    #endif

    fprintf(stdout, "The square root of %g is %g\n",
        inputvalue,outputvalue);
    return 0;
}