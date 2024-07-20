#include <iostream>
#include "VX_Object.h"
#include "VX_Environment.h"
#include "VX_Sim.h"
#include "VX_SimGA.h"
#include "VX_MeshUtil.h"
#include "VXS_SimGLView.h"

#include <string>
#include <stdio.h>
#include <stdlib.h>
#include <sstream>
#include <iomanip>

#include <iostream>
#include <fstream>
#include <math.h>
#include <cmath> 
#include <time.h>
using namespace std;

#include "Utils/XML_Rip.h"

#ifdef USE_OPEN_GL
#include "Utils/GL_Utils.h"
#endif

#ifdef _WIN32
#include <Windows.h>
#else
#include <unistd.h>
#endif

// function for saving the simulation results in a given bandwidth with step number
int save_positions_with_step_number(CVX_SimGA Simulator, char* InputFile, int step){

	std::string delimiter = "/";
	std::string mySaveFile = "";

	size_t pos = 0;
	std::string token;
	std::string myStringVXA(InputFile);

	while ((pos = myStringVXA.find(delimiter)) != std::string::npos) {
	    token = myStringVXA.substr(0, pos);
			myStringVXA.erase(0, pos + delimiter.length());
			if (token == "voxelyzeFiles") break;
			mySaveFile = mySaveFile + token + "/";
	}
	pos = myStringVXA.find(".");
	token = myStringVXA.substr(0, pos);
	mySaveFile = mySaveFile + "fitnessFiles/" + token + "_" + to_string(step) + ".xml";
	
	Simulator.SaveResultFile(mySaveFile);

	return 1;
}

int nsleep(long milliseconds)
{
   struct timespec req, rem;

   if(milliseconds > 999)
   {   
        req.tv_sec = (int)(milliseconds / 1000);                            /* Must be Non-Negative */
        req.tv_nsec = (milliseconds - ((long)req.tv_sec * 1000)) * 1000000; /* Must be in range of 0 to 999999999 */
   }   
   else
   {   
        req.tv_sec = 0;                         /* Must be Non-Negative */
        req.tv_nsec = milliseconds * 1000000;    /* Must be in range of 0 to 999999999 */
   }   

   return nanosleep(&req , &rem);
}


int main(int argc, char *argv[])
{
	char* B_ExtString;
	vfloat B_Ext;
	bool isB_Ext_provided = false;

	char* InputFile;
	char* MagnetizationInputFile;
	char* BFieldInputFile;

	//create the main objects
	CVXC_Structure structure;
	CVX_Object Object;
	CVX_Environment Environment;
	CVX_SimGA Simulator;
	CVX_MeshUtil DeformableMesh;
	long int Step = 0;
	vfloat Time = 0.0; //in seconds
	bool print_scrn = false;
	bool computeShapeDescriptors = false;

	//first, parse inputs. Use as: -f followed by the filename of the .vxa file that describes the simulation. Can also follow this with -p to cause console output to occur
	if (argc < 3)
	{ // Check the value of argc. If not enough parameters have been passed, inform user and exit.
		std::cout << "\nInput file required. Quitting.\n";
		return(0);	//return, indicating via code (0) that we did not complete the simulation
	}
	else
	{ // if we got enough parameters...
		for (int i = 1; i < argc; i++)
		{
			if (strcmp(argv[i],"-f") == 0)
			{
				InputFile = argv[i + 1];	// We know the next argument *should* be the filename:
			}
			else if (strcmp(argv[i],"-p") == 0)
			{
				print_scrn=true;	//decide if output to the console is desired
			}
			else if (strcmp(argv[i],"-B_ext") == 0)   //TODO: do this in .vxa file read&write
			{
				B_ExtString=argv[i + 1];	// We know the next argument *should* be the B_Ext:
				isB_Ext_provided = true;
				std::string fs(B_ExtString);
				B_Ext=std::stof(B_ExtString);
			}
			else if (strcmp(argv[i],"--computeShapeDescriptors") == 0)
			{
				computeShapeDescriptors = true;
			}
		}
	}

	//setup main object
	Simulator.pEnv = &Environment;	//connect Simulation to environment
	Environment.pObj = &Object;		//connect environment to object
	Simulator.setInternalMesh(&DeformableMesh);

	//import the configuration file
	if (!Simulator.LoadVXAFile(InputFile)){
		if (print_scrn) std::cout << "\nProblem importing VXA file. Quitting\n";
		return(0);	//return, indicating via code (0) that we did not complete the simulation
		}
	std::string ReturnMessage;
	if (print_scrn) std::cout << "\nImporting Environment into simulator...\n";

	Simulator.Import(&Environment, 0, &ReturnMessage);
	if (print_scrn) std::cout << "Simulation import return message:\n" << ReturnMessage << "\n";

	Simulator.pEnv->UpdateCurTemp(Time);	//set the starting temperature (nac: pointer removed for debugging)


	double hulVolumeStart, hulVolumeEnd, robotVolumeStart, robotVolumeEnd, sComplexityStart, sComplexityEnd;

	DeformableMesh.initializeDeformableMesh(&Simulator); // Initialize internal mesh and link it to the simulation

	if(computeShapeDescriptors)
	{
		hulVolumeStart = DeformableMesh.computeAndStoreQHullStart();
		robotVolumeStart = DeformableMesh.computeAndStoreRobotVolumeStart();
		sComplexityStart = DeformableMesh.computeInitialShapeComplexity();

		if (print_scrn)
		{
			std::cout << "Robot mesh has " << DeformableMesh.getMeshVertNum() << " vertices and " << DeformableMesh.getMeshFacetsNum() << " facets" << std::endl
					  << "Init robot volume: " << robotVolumeStart << std::endl
					  << "Init convex hull volume: " << hulVolumeStart << std::endl << std::endl
					  << "Init shape complexity: " << sComplexityStart << std::endl;

			DeformableMesh.printAllMeshInfo();
		}
	}

	int iT = Simulator.NumVox();
	CXML_Rip XML;

	/* Read the magnetization profile and controller type info */
	std::string myString(InputFile);
	int sizeOfFileName = myString.size();
	myString[sizeOfFileName-4] = '_';
	myString[sizeOfFileName-3] = 'M';
	myString[sizeOfFileName-2] = '.';
	myString[sizeOfFileName-1] = 'x';
	myString = myString + "ml";

	MagnetizationInputFile = &myString[0];

	XML.LoadFile(MagnetizationInputFile);
	CXML_Rip* pXML;
	pXML = &XML;

	pXML->FindElement("VoxelMProfile");
	string controller_type="quasi-static";

	if (pXML->FindLoadElement("ControllerType", &controller_type)){
		B_Ext = 0.;
		isB_Ext_provided = true;
		pXML->FindLoadElement("StaticBMag", &B_Ext);
	}
	
	double MperVol = 0.;
	pXML->FindLoadElement("MperVol", &MperVol);
	double KinEThreshold = 0.;
	pXML->FindLoadElement("KinEThreshold", &KinEThreshold);
	int isMagForceOn = 0;
	pXML->FindLoadElement("IsMagForceOn", &isMagForceOn);
	

	// load the settings for what to save
	pXML->FindLoadElement("SavePosition", &Simulator.isSavePosition);
	pXML->FindLoadElement("SaveOrientation", &Simulator.isSaveOrientation);
	pXML->FindLoadElement("SaveVelocity", &Simulator.isSaveVelocity);
	pXML->FindLoadElement("SaveAngVel", &Simulator.isSaveAngVel);
	pXML->FindLoadElement("SaveStrainEnergy", &Simulator.isSaveStrainEnergy);
	pXML->FindLoadElement("SaveKineticEnergy", &Simulator.isSaveKineticEnergy);
	pXML->FindLoadElement("SavePressure", &Simulator.isSavePressure);
	pXML->FindLoadElement("SaveForce", &Simulator.isSaveForce);


	// specific demonstarations and related initializations
	pXML->FindLoadElement("CaseMaxCOMZPos", &Simulator.isCaseMaxCOMZPos);
	if (print_scrn) std::cout << "Simulator.isCaseMaxCOMZPos is set to \n" << Simulator.isCaseMaxCOMZPos <<"\n";
	pXML->FindLoadElement("CaseMaxMinPosZ", &Simulator.isCaseMaxMinPosZ);
	Vec3D<double> curCOM = Vec3D<>(0,0,0);
	Vec3D<double> curCOMvel = Vec3D<>(0,0,0);
	Vec3D<double> curMaxMinPosZ = Vec3D<>(0,0,0);
	int minVoxNum_touchingFloor = 999999;
	pXML->FindLoadElement("Is3D", &Simulator.isDemo3D);
	bool is1stPartDone = false;


	// check if a video data is required
	bool isRecordVideo = false;
	double videoBW = 0.;
	pXML->FindLoadElement("IsRecordVideo", &isRecordVideo);
	pXML->FindLoadElement("VideoBW", &videoBW);


	// check if recording a history file for detailed position info that can be used for visualization
	bool isCreateHistory = false;
	double historyBW = 0.;
	int history_stepsize = 0; 
	double rescale = 0;
	vfloat vox_vol = 0.0;
	ofstream outFile;
	std::string myHistoryFile = "";
	pXML->FindLoadElement("IsCreateHistory", &isCreateHistory);
	pXML->FindLoadElement("HistoryBW", &historyBW);

	if (isCreateHistory){
		std::string delimiter_history = "/";
		
		size_t pos = 0;
		std::string token_hist;
		std::string myStringVXA(InputFile);

		while ((pos = myStringVXA.find(delimiter_history)) != std::string::npos) {
			token_hist = myStringVXA.substr(0, pos);
				myStringVXA.erase(0, pos + delimiter_history.length());
				if (token_hist == "voxelyzeFiles") break;
				myHistoryFile = myHistoryFile + token_hist + "/";
		}
		pos = myStringVXA.find(".");
		token_hist = myStringVXA.substr(0, pos);
		myHistoryFile = myHistoryFile + "fitnessFiles/" + token_hist + "_history"  ".txt";


		vox_vol =  pow(Simulator.VoxArray[0].GetNominalSize(), 3.0);
	}


	// video settings
	int video_counter = 0;
	double video_dt=0.;
	double video_next_time = 0.;
	if (isRecordVideo){
		video_dt=1./videoBW;
		video_next_time = video_dt*video_counter;
	}
	
	// check if the magnetic force is to be included - if force is on, permanent magnet is utilized, if OFF electromagnet coil setup
	if (isMagForceOn) {Simulator.TurnMagneticForceOn(); if (print_scrn) {std::cout << "== Magnetic Force Turned ON ==" << std::endl;}}
	else {Simulator.TurnMagneticForceOff(); if (print_scrn) {std::cout << "== Magnetic Force Turned OFF ==" << std::endl;}}


	// read the magnetization direction of the voxels
	pXML->FindElement("VoxelMagnetizations");
	double Mx = 0.;
	double My = 0.;
	double Mz = 0.;
	for (int i=0; i<iT; i++){
		if (pXML->FindElement("VoxelNum" + std::to_string(i))){
				pXML->FindLoadElement("VoxelMx", &Mx);
				pXML->FindLoadElement("VoxelMy", &My);
				pXML->FindLoadElement("VoxelMz", &Mz);
				pXML->UpLevel();

				Simulator.VoxArray[i].SetInitMDirec(Vec3D<double>(Mx,My,Mz));
				Simulator.VoxArray[i].SetCurMDirec(Vec3D<double>(Mx,My,Mz));
				Simulator.VoxArray[i].SetCurMoment(Simulator.VoxArray[i].GetCurMMagnitude()*Simulator.VoxArray[i].GetCurMDirec());

				if (print_scrn) std::cout << "MMagnitude: " << Simulator.VoxArray[i].GetCurMMagnitude() << std::endl;
				if (print_scrn) std::cout << "\nMmoment in X: " << Simulator.VoxArray[i].GetCurMoment().x << " Y: " <<Simulator.VoxArray[i].GetCurMoment().y << " Z: " <<Simulator.VoxArray[i].GetCurMoment().z << "\n" << std::endl;

	  }
		// check if external magnetic field values is provided -- quasi-static B field case
		if (isB_Ext_provided) {
			Simulator.VoxArray[i].SetCurBExt(Vec3D<double>(0,0,B_Ext));
		}
		else {
			B_Ext = 30e-3;  // default value --> 30mT
			Simulator.VoxArray[i].SetCurBExt(Vec3D<double>(0,0,B_Ext));
		}
	}


	// controller parameters for open-loop or closed-loop control 
	double B_period=0.;
	double time_record_period_next_time = 0.;
	double B_controller_bandwidth=0.;
	int BStreamNum=0.;
	int B_control_counter = 0;
	double B_control_dt=0.;
	double B_control_next_time = 0.;
	bool isPrintEveryStep = false;

	// set the file path for magnetic field
	std::string _myString(InputFile);
	int _sizeOfFileName = _myString.size();
	_myString[_sizeOfFileName-4] = '_';
	_myString[_sizeOfFileName-3] = 'B';
	_myString[_sizeOfFileName-2] = '.';
	_myString[_sizeOfFileName-1] = 'x';
	_myString = _myString + "ml";
	BFieldInputFile = &_myString[0];


	if (controller_type == "open-loop"){
		CXML_Rip XML;
		/* Read the magnetic field info */
		XML.LoadFile(BFieldInputFile);
		CXML_Rip* pXML;
		pXML = &XML;
	
		// Read the controller settings
		if (controller_type == "open-loop"){
			pXML->FindElement("MagneticField");
			pXML->FindLoadElement("B_period", &B_period);
			pXML->FindLoadElement("B_controller_bandwidth", &B_controller_bandwidth);
			pXML->FindLoadElement("BStreamNum", &BStreamNum);
			pXML->FindLoadElement("isPrintEveryStep", &isPrintEveryStep);
		} 
		B_control_dt=1./B_controller_bandwidth;
		B_control_next_time = B_control_dt*B_control_counter;
		time_record_period_next_time = 0.;
	}


	double B[BStreamNum][3]{};
	// Read the open-loop magnetic field (B) stream
	if (controller_type == "open-loop"){
		CXML_Rip XML;
		/* Read the magnetic field info */
		XML.LoadFile(BFieldInputFile);
		CXML_Rip* pXML;
		pXML = &XML;

		pXML->FindElement("MagneticField");
		pXML->FindElement("BStream");
		double Bx = 0.;
		double By = 0.;
		double Bz = 0.;
		
		for (int i = 0; i<BStreamNum; i++){
			if(pXML->FindElement("BNum"+ std::to_string(i))){
				pXML->FindLoadElement("Bx", &Bx);
				pXML->FindLoadElement("By", &By);
				pXML->FindLoadElement("Bz", &Bz);
				pXML->UpLevel();
				B[i][0] = Bx;
				B[i][1] = By;
				B[i][2] = Bz;
			}
		}
	}


	// write the settings for the history file
	if (isCreateHistory) { // output History file

		outFile.open(myHistoryFile);
		// rescale the whole space. so history file can contain less digits. ( e.g. not 0.000221, but 2.21 )
		rescale = 1 / 0.001;
		outFile << "\n{{{setting}}}<rescale>0.001</rescale>\n";

		// set materials' color
		int mat_num = Simulator.LocalVXC.GetNumMaterials();
		int mat_labeled[mat_num] = {0};
		bool found;
		for (int i = 0; i < iT; i++) {
			int matid = Simulator.VoxArray[i].GetMaterialIndex();
			found = false;
			for (int j = 0; j < mat_num; j++) {
				if (mat_labeled[j] == matid) {
					found = true;
					break; // Exit the loop early if the number is found
				}
			}
			if (!found){ 
				mat_labeled[matid-1]= matid;
				float red = Simulator.VoxArray[i].GetpMaterial()->GetRedf();
				float green = Simulator.VoxArray[i].GetpMaterial()->GetGreenf();
				float blue = Simulator.VoxArray[i].GetpMaterial()->GetBluef();
				float alpha = Simulator.VoxArray[i].GetpMaterial()->GetAlphaf();
				outFile << "{{{setting}}}<matcolor><id>"<< matid <<"</id><r>"<< red << "</r><g>" << green << "</g><b>"<<blue<< "</b><a>"<<alpha<< "</a></matcolor>\n";
				}
		}
		
		outFile << "\n{{{setting}}}<voxel_size>"<< Simulator.VoxArray[0].GetNominalSize() <<"</voxel_size>\n";

		// step size calculations
		float history_stepDt = 1./historyBW;
		history_stepsize = int(history_stepDt/(Simulator.OptimalDt*Simulator.DtFrac))+1;

		//delete later -- some extra information for double checking
		std::cout << "history_stepDt: " << history_stepDt << std::endl;
		std::cout << "Simulator.DtFrac " << Simulator.DtFrac << std::endl;
		std::cout << "historyBW: " << historyBW << std::endl;
		std::cout << "Simulator.OptimalDt: " << Simulator.OptimalDt << std::endl;
		std::cout << "myHistoryFile: " << myHistoryFile << std::endl;
		std::cout << "history_stepsize: " << history_stepsize << std::endl;

        outFile << "real_stepsize: "<<history_stepsize<<" ; recommendedTimeStep "<< Simulator.OptimalDt <<"; d_v3->DtFrac "<< Simulator.DtFrac <<" . \n";

		Simulator.TurnMagneticForceOff();
    }

	
	/* 
	*** Start the simulation iterations ***
	*/ 
	vfloat KinEAvg = 0.;
	while (not Simulator.StopConditionMet())
	{
		
		// save video data
		if (isRecordVideo){
			if(Time == 0. || Time > video_next_time){	
				// also save the current position with a controller step stamp
				save_positions_with_step_number(Simulator, InputFile, video_counter);
				video_counter++;
				video_next_time = video_dt*video_counter;
			}			
		}

		// save history data
		if (isCreateHistory){
			if(Step%history_stepsize==0){	
				// ofstream outFile;
				outFile << std::fixed <<std::setprecision(4) << float(3.566666) << "\n\n";
				// Voxels
				outFile << "<<<Step"<<Step<<" Time:" << Time << ">>>";
				for (int i = 0; i < iT; i++) {
					Vec3D<double> Pos = Simulator.VoxArray[i].GetCurPos();
					Quat3D<double> Orientation = Simulator.VoxArray[i].GetCurAngle();

					outFile << Pos.x * rescale << "," << Pos.y * rescale << "," << Pos.z * rescale << ",";
					outFile << Orientation.AngleDegrees() << "," << Orientation.x << "," << Orientation.y << "," << Orientation.z << ",";

					Vec3D<double> ppp, nnn;
					nnn = Simulator.VoxArray[i].GetCornerNeg();
					ppp = Simulator.VoxArray[i].GetCornerPos();
					outFile << nnn.x*rescale<<","<<nnn.y*rescale<<","<<nnn.z*rescale<<","<<ppp.x*rescale<<","<<ppp.y*rescale<<","<<ppp.z*rescale<<",";
					outFile << Simulator.VoxArray[i].GetMaterialIndex() <<","; // for coloring
					outFile << Simulator.VoxArray[i].GetMaxBondStrainE()/vox_vol <<","; // for Strain Energy Density
					outFile << ";";
				}
				outFile << "<<<>>>";
			}			
		}

		// do some reporting via the stdoutput if required:
		if (Step%500 == 0.0 && print_scrn) //Only output every n time steps
		{	
			// printing for debugging purposes
			std::cout << "Time: " << Time << std::endl;
			// std::cout << "CM: " << Simulator.GetCM().Length() << std::endl << std::endl;
			std::cout << " \tVox end X: " << Simulator.VoxArray[iT-1].GetCurPos().x << "mm" << "\tVox 0 Y: " << Simulator.VoxArray[iT-1].GetCurPos().y << "mm" << "\tVox 0 Z: " << Simulator.VoxArray[iT-1].GetCurPos().z << "mm\n";	//just display the position of the first voxel in the voxelarray
			std::cout << " \tVox 0 X: " << Simulator.VoxArray[0].GetCurPos().x << "mm" << "\tVox 0 Y: " << Simulator.VoxArray[0].GetCurPos().y << "mm" << "\tVox 0 Z: " << Simulator.VoxArray[0].GetCurPos().z << "mm\n";	//just display the position of the first voxel in the voxelarray
			std::cout << "Total Kin. Energy: " << Simulator.KinEHistory[0] << std::endl;
			std::cout << "Strain Energy: " << Simulator.VoxArray[0].GetMaxBondStrainE() << std::endl;
		}


		// set the exteral B field if controller in action
		if (controller_type != "quasi-static"){
			if (controller_type == "open-loop"){
				if(Time == 0. || Time > B_control_next_time){

					int B_index = B_control_counter%BStreamNum;

					for (int i=0; i<iT; i++){
						Simulator.VoxArray[i].SetCurBExt(Vec3D<double>(B[B_index][0],B[B_index][1],B[B_index][2]));
					}		

					// also save the current position with a controller step stamp
					if (isPrintEveryStep) {
						save_positions_with_step_number(Simulator, InputFile, B_control_counter);
					}

					// delete this if depreciated
					if (B_period>Time && Time>B_period*0.90){
						
						save_positions_with_step_number(Simulator, InputFile, -1);
					}


					B_control_counter++;
					B_control_next_time = B_control_dt*B_control_counter;
				}
			} 
			else if(controller_type == "closed-loop"){

				if(Time == 0. || Time > B_control_next_time){
					CXML_Rip XML;

					// set the closed loop controller file path for this step
					std::string _myString(InputFile);
					int sizeOfFileName = _myString.size();
					_myString[sizeOfFileName-4] = '_';
					_myString[sizeOfFileName-3] = 'B';
					_myString[sizeOfFileName-2] = 's';
					_myString[sizeOfFileName-1] = 't';
					_myString = _myString + "ep_" + to_string(B_control_counter) + ".xml";
					char* _BField_CL_InputFile;
					_BField_CL_InputFile = &_myString[0];

					// save the current position with a controller step stamp so that the controller decides accordinly
					save_positions_with_step_number(Simulator, InputFile, B_control_counter);

					while(!XML.LoadFile(_BField_CL_InputFile)){
						// sleep if the B file is not there yet
						if(print_scrn){
							std::cout << "\n\nWaiting for the Bstep file\n\n" << std::endl;
						}
						nsleep(100); // sleep for 200ms
					}

					// Read the file
					CXML_Rip* pXML;
					pXML = &XML;

					pXML->FindElement("MagneticField");
					if(B_controller_bandwidth == 0){
						pXML->FindLoadElement("B_controller_bandwidth", &B_controller_bandwidth);
						B_control_dt=1./B_controller_bandwidth;
						B_control_next_time = B_control_dt*B_control_counter;
					}	

					double Bx = 0.;
					double By = 0.;
					double Bz = 0.;
					
					if(pXML->FindElement("BNum"+ std::to_string(0))){
						pXML->FindLoadElement("Bx", &Bx);
						pXML->FindLoadElement("By", &By);
						pXML->FindLoadElement("Bz", &Bz);
						pXML->UpLevel();
					}
					
					for (int i=0; i<iT; i++){
						Simulator.VoxArray[i].SetCurBExt(Vec3D<double>(Bx,By,Bz));
					}		

					B_control_counter++;
					B_control_next_time = B_control_dt*B_control_counter;
				}
			}
		}

		//  *** do the actual simulation step  ***
		if (!Simulator.TimeStep(&ReturnMessage)){
			std::cout << "\n\nSimulation diverged, QUITING!\n\n" << std::endl;
			break;
		}

		Step += 1;	//increment the step counter
		Time += Simulator.dt;	//update the sim time after the step
		Simulator.pEnv->UpdateCurTemp(Time);	//pass in the global time, and a pointer to the local object so its material temps can be modified (nac: pointer removed for debugging)

		// keep track of the average Kinetic energy of the simulated body --> this values is used for the determination in quasi-static cases
		if (Step>100){
			KinEAvg = (Simulator.KinEHistory[0]+Simulator.KinEHistory[1]+Simulator.KinEHistory[2]+Simulator.KinEHistory[3]+Simulator.KinEHistory[4]+Simulator.KinEHistory[5])/6;
		}

		// controller actions specific to demonstration cases
		if (controller_type == "quasi-static"){
		
			if (Simulator.isCaseMaxCOMZPos){
				if (not is1stPartDone){
					if ((KinEAvg < KinEThreshold && Step>750 && Step%50 == 0.0 ) || Simulator.StopConditionMet()){
						is1stPartDone = true;
						if (print_scrn) std::cout << "Simulation 1st part is completed \n" << "\n";

						// extent the sim max time for the 2nd part
						if (controller_type == "quasi-static") {
							Simulator.SetStopConditionValue(2*Simulator.GetStopConditionValue());
						}

						int VoxNum_touchingFloor = Simulator.GetNumTouchingFloor();
						Simulator.minVoxNum_touchingFloor = VoxNum_touchingFloor;
					
						// save the position at the change moment
						save_positions_with_step_number(Simulator, InputFile, -1);

						if (Simulator.isCaseMaxCOMZPos) {   // set the external B field
							for (int i=0; i<iT; i++){
								Simulator.VoxArray[i].SetCurBExt(Vec3D<double>(0,0,-B_Ext));
							}
							if (print_scrn) std::cout << "B field is reversed\n" << "\n";
						}
					}
				}
				else if (is1stPartDone && Simulator.isCaseMaxCOMZPos && Step%20 == 0.0){
					
					curCOM = Simulator.GetCM();
					if (curCOM.z > Simulator.COM_maxZ.z){
						Simulator.COM_maxZ = curCOM;
						save_positions_with_step_number(Simulator, InputFile, -2);
					}

					if (Simulator.isCaseMaxMinPosZ){
						curMaxMinPosZ = Simulator.GetMaxMinPosZ();
						if (curMaxMinPosZ.z > Simulator.MaxMinPosZ.z){
							Simulator.MaxMinPosZ = curMaxMinPosZ;
							save_positions_with_step_number(Simulator, InputFile, -3);
						}
					}

					minVoxNum_touchingFloor = Simulator.GetNumTouchingFloor();
					
					if (minVoxNum_touchingFloor < Simulator.minVoxNum_touchingFloor){
						Simulator.minVoxNum_touchingFloor = minVoxNum_touchingFloor;
					}

					if (minVoxNum_touchingFloor<1){
						Simulator.isSampleOnAir = true;
					}
					else{
						Simulator.isSampleOnAir = false;	
					}

					if (Simulator.isSampleOnAir){
						Simulator.sampleAirTotStep += 20;
					}
					
				}
				else if (is1stPartDone && Step%250 == 0.0 && Step>1500 && controller_type == "quasi-static") {
					// is steady state achieved? quasi-static result obtained or not?
					// end the simulation if Kinetic energy is lower than the set threshold
					if (KinEAvg < KinEThreshold ) break;
				}
			}
			// is steady state achieved? quasi-static result obtained or not?
			else if ( Step%250 == 0.0 && Step>1500 && controller_type == "quasi-static") {
				if (KinEAvg < KinEThreshold ) break;
			}
			
			}
		else if (controller_type == "open-loop"){

			if (Time>time_record_period_next_time) {
					curCOM = Simulator.GetCM();
					Simulator.walkerCOMXs.push_back(curCOM.x);
					time_record_period_next_time = time_record_period_next_time + B_period;
				}

			if (Simulator.isCaseMaxCOMZPos){
				if (not is1stPartDone){
					if (Time>B_period){
						is1stPartDone = true;
						if (print_scrn) std::cout << "Simulation 1st part is completed \n" << "\n";
						int VoxNum_touchingFloor = Simulator.GetNumTouchingFloor();
						Simulator.minVoxNum_touchingFloor = VoxNum_touchingFloor;
						// save the position at the change moment
						save_positions_with_step_number(Simulator, InputFile, -1);
					}
				}
				else if (is1stPartDone && Simulator.isCaseMaxCOMZPos && Step%20 == 0.0){
					
					curCOM = Simulator.GetCM();
					if (curCOM.z > Simulator.COM_maxZ.z){
						Simulator.COM_maxZ = curCOM;
						save_positions_with_step_number(Simulator, InputFile, -2);
					}

					if (Simulator.isCaseMaxMinPosZ){
						curMaxMinPosZ = Simulator.GetMaxMinPosZ();
						if (curMaxMinPosZ.z > Simulator.MaxMinPosZ.z){
							Simulator.MaxMinPosZ = curMaxMinPosZ;
							save_positions_with_step_number(Simulator, InputFile, -3);
						}
					}

					minVoxNum_touchingFloor = Simulator.GetNumTouchingFloor();

					if (minVoxNum_touchingFloor < Simulator.minVoxNum_touchingFloor){
						Simulator.minVoxNum_touchingFloor = minVoxNum_touchingFloor;
					}

					if (minVoxNum_touchingFloor<1){
						Simulator.isSampleOnAir = true;	
					}
					else{
						Simulator.isSampleOnAir = false;	
					}

					if (Simulator.isSampleOnAir){
						Simulator.sampleAirTotStep += 20;
					}
					
				}
				
			}
			else if (Step%20 == 0.0){

				minVoxNum_touchingFloor = Simulator.GetNumTouchingFloor();
				
				if (minVoxNum_touchingFloor < Simulator.minVoxNum_touchingFloor){
					Simulator.minVoxNum_touchingFloor = minVoxNum_touchingFloor;
				}

				if (minVoxNum_touchingFloor<1){
					Simulator.isSampleOnAir = true;
				}
				else{
					Simulator.isSampleOnAir = false;	
				}

				if (Simulator.isSampleOnAir){
					Simulator.sampleAirTotStep += 20;
				}
			}
		}
	}

	Simulator.sampleAirTotTime = Simulator.sampleAirTotStep*Simulator.OptimalDt*Simulator.DtFrac;

	if (controller_type != "quasi-static"){
		// also save the current position with a controller step stamp
		if (isPrintEveryStep) {
			save_positions_with_step_number(Simulator, InputFile, B_control_counter);
		}
	}

	if(computeShapeDescriptors)
	{
		hulVolumeEnd = DeformableMesh.computeAndStoreQHullEnd();
		robotVolumeEnd = DeformableMesh.computeAndStoreRobotVolumeEnd();
		sComplexityEnd = DeformableMesh.computeFinalShapeComplexity();

		if (print_scrn)
		{
			std::cout << "Final robot volume: " << robotVolumeEnd << std::endl
					  << "Final convex hull volume: " << hulVolumeEnd << std::endl << std::endl
					  << "Final shape complexity: " << sComplexityEnd << std::endl;
  			DeformableMesh.printAllMeshInfo();
  		}
	}

	if (print_scrn) std::cout << "Ended at: " << Time << std::endl;

	std::ostringstream os;
	os << B_Ext;

	std::string delimiter = "/";
	std::string mySaveFile = "";

	size_t pos = 0;
	std::string token;
	std::string myStringVXA(InputFile);

	while ((pos = myStringVXA.find(delimiter)) != std::string::npos) {
		token = myStringVXA.substr(0, pos);
			myStringVXA.erase(0, pos + delimiter.length());
			if (token == "voxelyzeFiles") break;
			mySaveFile = mySaveFile + token + "/";
	}
	pos = myStringVXA.find(".");
	token = myStringVXA.substr(0, pos);
	mySaveFile = mySaveFile + "fitnessFiles/" + token + ".xml";

	Simulator.SaveResultFile(mySaveFile);

	if (print_scrn) std::cout << "File name: " << mySaveFile << std::endl;

	if (isCreateHistory){
		outFile.close();
	}
		

	return 1;	//code for successful completion  // could return fitness value if greater efficiency is desired
}
