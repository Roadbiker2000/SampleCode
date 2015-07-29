#include <stdio.h>
#include <stdlib.h>
#include <Fourier.h>
#include <cmdLineParser.h>


/* THIS FILE WILL NOT COMPILE AS IS */
/* A number of both simple source files as well as external libraries such as FFTW are required as well as a number of other source files*/

/*
void ForwardFT(const CircularArray<>& values,Complex<>* coeffs){

	for (int i = 0, n = values.resolution(); i < n; i++) {
		for (int j = 0; j < n; j++) {
			double angle = 2 * PI * (double) i * (double) j / (double) n;

			coeffs[i].r += values(j) * cos(angle);
			coeffs[i].i -= values(j) * sin(angle);
		}
	}
	
}
*/
Complex<>* ForwardFFT2(Complex<>* coeffs, int N){

	if (N % 2 != 0) {
		if (N != 1) {printf("remember to fil n mod 2\n");}
		// return ForwardFT(coeffs, N);
		return coeffs;
	}

	Complex<>* even = new Complex<>[N / 2];
	Complex<>* odd  = new Complex<>[N / 2];

	for (int i = 0; i < N / 2; i++) {
		even[i] = coeffs[2*i];
		odd[i]  = coeffs[2*i+1];
	}

	Complex<>* q = ForwardFFT2(even, N / 2);
	Complex<>* r = ForwardFFT2(odd, N / 2);

	Complex<>* merge = new Complex<>[N];

	for (int i = 0; i < N / 2; i++) {

		double angle = -2.0 * (double) i * PI / (double) N;
		
		merge[i].r = cos(angle);
		merge[i].i = sin(angle);

		merge[i] *= r[i];
		merge[i] += q[i];

		merge[i + N / 2].r = cos(angle);
		merge[i + N / 2].i = sin(angle);

		merge[i + N / 2] *= r[i];
		merge[i + N / 2] *= -1;
		merge[i + N / 2] += q[i];

	}

	return merge;
}

void ForwardFFT(const CircularArray<>& values,Complex<>* coeffs){
 	
	Complex<>* in_array = new Complex<>[values.resolution()];
	for (int i = 0, N = values.resolution(); i < N; i++) {
		in_array[i].r = values(i);
	}

	in_array = ForwardFFT2(in_array, values.resolution());
	
	for (int i = 0, N = values.resolution(); i < N; i++) {
		coeffs[i].r = in_array[i].r;
		coeffs[i].i = in_array[i].i;

	}
}

// void InverseFT(const Complex<>* coeffs,CircularArray<>& values){

// 	for (int i = 0, n = values.resolution(); i < n; i++) {
// 		for (int j = 0; j < n; j++) {
		
// 			double angle = 2 * PI * (double) i * (double) j / (double) n;		
// 			values(i) += coeffs[j].r * cos(angle) - coeffs[j].i * sin(angle);
		
// 		}
// 	}
// }


void InverseFFT(const Complex<>* coeffs,CircularArray<>& values){

	int N = values.resolution();
	
	Complex<>* conjugates = new Complex<>[N];

	// take conjugate
	for (int i = 0; i < N; i++) {
		conjugates[i] = coeffs[i].conjugate();
	}

	// compute forward FFT
	conjugates = ForwardFFT2(conjugates, N);

	// take conjugate again
	for (int i = 0; i < N; i++) {
		values(i) = conjugates[i].conjugate().r;
	}
}

int main(int argc,char* argv[]){
	// Read the parameters in from the command line
	cmdLineString In;
	char* paramNames[]={"in"};
	cmdLineReadable* params[]={&In};
	cmdLineParse(argc-1,&argv[1],paramNames,sizeof(paramNames)/sizeof(char*),params);
	if(!In.set){
		fprintf(stderr,"You must specify an input file\n");
		return EXIT_FAILURE;
	}

	int res;
	float l2;
	CircularArray<> cIn,cOut;
	Complex<>* coeffs;

	// Read in the array
	cIn.read(In.value);
	res=cIn.resolution();

	// Allocate space for the Fourier coefficients
	coeffs=new Complex<>[res];

	// Run the forward and inverse Fourier transforms
	cOut.resize(res);
	ForwardFFT(cIn,coeffs);
	InverseFFT(coeffs,cOut);
	// Correct for the scaling term

	for(int i=0;i<res;i++){cOut(i)/=res;}

	// Test that the Fourier coefficients satisfy the conjugacy relations (difference should be zero)
	l2=0;
	for(int i=0;i<res;i++){l2+=(coeffs[i]-coeffs[(res-i)%res].conjugate()).squareNorm();}
	printf("Conjugate Test: %f\n",l2);



	// Compare the input and output (the difference should be zero)
	printf("Forward-Inverse Test: %f\n",CircularArray<>::SquareDifference(cIn,cOut));

	// Now compare the values of the Fourier coefficients (difference should be zero)
	FourierKey1D<> key;
	FourierTransform<> xForm;

	xForm.ForwardFourier(cIn,key);

	l2=0;
	float n=float(1.0/(2.0*PI))*key.resolution();

	// for(int i=0;i<32;i++){
	// for(int i=0;i<key.size();i++){
		// printf("%d kr: %-15f ki: %-15f cr: %-15f ci: %-15f diff: %f\n", i, key(i).r*n, key(i).i*n, coeffs[i].r, coeffs[i].i, key(i)*n - coeffs[i]);
	// } 

	for(int i=0;i<key.size();i++){l2+=(key(i)*n-coeffs[i]).squareNorm();}
	printf("Coefficient test: %f\n",l2);

	return EXIT_SUCCESS;
}