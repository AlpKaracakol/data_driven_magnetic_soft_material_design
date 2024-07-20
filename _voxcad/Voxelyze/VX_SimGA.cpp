/*******************************************************************************
Copyright (c) 2010, Jonathan Hiller (Cornell University)
If used in publication cite "J. Hiller and H. Lipson "Dynamic Simulation of Soft Heterogeneous Objects" In press. (2011)"

This file is part of Voxelyze.
Voxelyze is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Voxelyze is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
See <http://www.opensource.org/licenses/lgpl-3.0.html> for license details.
*******************************************************************************/

#include "VX_SimGA.h"
#include <iostream>

CVX_SimGA::CVX_SimGA()
{
	Fitness = 0.0f;
	TrackVoxel = 0;
	FitnessFileName = "";
//	print_scrn = false;
	WriteFitnessFile = false;
	FitnessType = FT_NONE;	//no reporting is default

}

void CVX_SimGA::SaveResultFile(std::string filename)
{
	CXML_Rip XML;
	WriteResultFile(&XML);
	XML.SaveFile(filename);
}

void CVX_SimGA::WriteResultFile(CXML_Rip* pXML)
{

  double finalDist = pow(pow(SS.CurCM.x-IniCM.x,2)+pow(SS.CurCM.y-IniCM.y,2),0.5)/LocalVXC.GetLatticeDim();
	double normFinalDist = finalDist; // includes frozen time
	double normRegimeDist = SS.CurPosteriorDist - SS.EndOfLifetimePosteriorY;
	double normFrozenDist = 0;

	double finalDistY = (SS.CurCM.y-IniCM.y) / LocalVXC.GetLatticeDim();

	double FallAdjPostY = SS.EndOfLifetimePosteriorY;

    double PushDist = 0;
	int FoundNeedleInHaystack = 0;
	if (pEnv->GetUsingNeedleInHaystack())
	{
	    PushDist = pow(pow(SS.CurNeedlePos.x-InitialNeedlePosition.x,2)+pow(SS.CurNeedlePos.y-InitialNeedlePosition.y,2),0.5)/LocalVXC.GetLatticeDim();

	    if(SS.CurNeedlePos.x != InitialNeedlePosition.x or SS.CurNeedlePos.y != InitialNeedlePosition.y)
	    {
	    FoundNeedleInHaystack = 1;
	    }
	}

	if (pEnv->getUsingNormDistByVol())
	{
	    double thisDist;
	    double thisVol;
	    Vec3D<> lastCM = SS.CMTrace[0];
	    double lastVol = SS.VolTrace[0];
	    normFinalDist = 0;

	    for(std::vector<vfloat>::size_type i = 1; i != SS.VolTrace.size(); ++i)
	    {
            thisDist = (SS.CMTrace[i].y - lastCM.y) / LocalVXC.GetLatticeDim();
            thisVol = (SS.VolTrace[i] + lastVol) / 2;
            normFinalDist += thisDist / pow(thisVol, pEnv->GetNormalizationExponent());
            // std::cout << "normFinalDist: " << normFinalDist << "  thisVol: " << thisVol << std::endl;
            lastCM = SS.CMTrace[i];
            lastVol = SS.VolTrace[i];
	    }
	}

	if (pEnv->getUsingNormDistByVol() and (GetAfterlifeTime() > 0))
	{
	    double thisDist;
	    double thisVol;
	    Vec3D<> lastCM = SS.CMTraceAfterLife[0];
	    double lastVol = SS.VolTraceAfterLife[0];
	    normRegimeDist = 0;

	    for(std::vector<vfloat>::size_type i = 1; i != SS.VolTraceAfterLife.size(); ++i)
	    {
            thisDist = (SS.CMTraceAfterLife[i].y - lastCM.y) / LocalVXC.GetLatticeDim();
            thisVol = (SS.VolTraceAfterLife[i] + lastVol) / 2;
            normRegimeDist += thisDist / pow(thisVol, pEnv->GetNormalizationExponent());
            // std::cout << "normRegimeDist: " << normRegimeDist << "  thisVol: " << thisVol << std::endl;
            lastCM = SS.CMTraceAfterLife[i];
            lastVol = SS.VolTraceAfterLife[i];
	    }
	}

	if (pEnv->getUsingNormDistByVol() and (GetMidLifeFreezeTime() > 0))
	{
	    double thisDist;
	    double thisVol;
	    Vec3D<> lastCM = SS.CMTraceWhileFrozen[0];
	    double lastVol = SS.VolTraceWhileFrozen[0];
	    normFrozenDist = 0;

	    for(std::vector<vfloat>::size_type i = 1; i != SS.VolTraceWhileFrozen.size(); ++i)
	    {
            thisDist = (SS.CMTraceWhileFrozen[i].y - lastCM.y) / LocalVXC.GetLatticeDim();
            thisVol = (SS.VolTraceWhileFrozen[i] + lastVol) / 2;
            normFrozenDist += thisDist / pow(thisVol, pEnv->GetNormalizationExponent());
            // std::cout << "normFrozenDist: " << normFrozenDist << "  thisVol: " << thisVol << std::endl;
            lastCM = SS.CMTraceWhileFrozen[i];
            lastVol = SS.VolTraceWhileFrozen[i];
	    }
	}

    // std::cout << "height: " << pEnv->pObj->GetVZDim() << std::endl;
    if (pEnv->isFallingProhibited() && FellOver)  // it fell over
    {
        FallAdjPostY = SS.EndOfLifetimePosteriorY - pEnv->pObj->GetVZDim();
        //std::cout << "FallAdjPostY: " << FallAdjPostY << std::endl;

        normFinalDist = 0;
	    normRegimeDist = 0;
	    normFrozenDist = 0;

    }


//	if(pEnv->pObj->GetUsingFinalVoxelSize())
//	{
//		normFinalDist = pow(pow(SS.EndOfLifetimeCM.x-IniCM.x,2)+pow(SS.EndOfLifetimeCM.y-IniCM.y,2),0.5)/LocalVXC.GetLatticeDim();
////		normRegimeDist = pow(pow(SS.CurCM.x-SS.EndOfLifetimeCM.x,2)+pow(SS.CurCM.y-SS.EndOfLifetimeCM.y,2),0.5)/LocalVXC.GetLatticeDim();
//	}
//	else
//	{
//		normFinalDist = pow(pow(SS.CurCM.x-IniCM.x,2)+pow(SS.CurCM.y-IniCM.y,2),0.5)/LocalVXC.GetLatticeDim();
////		normRegimeDist = pow(pow(SS.CurCM.x-SS.RegimeStartCM.x,2)+pow(SS.CurCM.y-SS.RegimeStartCM.y,2),0.5)/LocalVXC.GetLatticeDim();
//	}



	pXML->DownLevel("Voxelyze_Sim_Result"); 

		pXML->SetElAttribute("Version", "1.0");

		pXML->DownLevel("CurTime");
			pXML->Element("CurTime(s)", GetCurTime());
		pXML->UpLevel();

		pXML->DownLevel("B external");

				pXML->Element("External Bx: ", VoxArray[0].GetCurBExt().x);
				pXML->Element("External By: ", VoxArray[0].GetCurBExt().y);
				pXML->Element("External Bz: ", VoxArray[0].GetCurBExt().z);

		pXML->UpLevel();
		

		pXML->DownLevel("JumpTime");
			
			pXML->Element("sampleAirTotTime: ", sampleAirTotTime);

		pXML->UpLevel();

		pXML->DownLevel("WalkerCOMXs");
			std::ostringstream oss;
			int _idx = 0;
			oss << ","; // Add a comma between values
			for (double element : walkerCOMXs) {
				oss <<  _idx;
				oss << ":"; // Add a comma between values
				oss << element;
				oss << ","; // Add a comma between values
				_idx++;
			}

			std::string WalkerCOMXsArraySTR = oss.str();
		
			pXML->Element("WalkerCOMXsArray: ", WalkerCOMXsArraySTR);
		pXML->UpLevel();

		if(isCaseMaxCOMZPos){
			pXML->DownLevel("COMmaxZ");
			
				pXML->Element("COMx: ", COM_maxZ.x);
				pXML->Element("COMy: ", COM_maxZ.y);
				pXML->Element("COMz: ", COM_maxZ.z);

			pXML->UpLevel();
			pXML->DownLevel("COMvelmaxVelZ");
			
				pXML->Element("COMvelx: ", COMvel_maxVelZ.x);
				pXML->Element("COMvely: ", COMvel_maxVelZ.y);
				pXML->Element("COMvelz: ", COMvel_maxVelZ.z);

			pXML->UpLevel();

			pXML->DownLevel("TouchingFloor");
			
				pXML->Element("voxNumTouchingFloor: ", minVoxNum_touchingFloor);

			pXML->UpLevel();

			pXML->DownLevel("JumpTime");
			
				pXML->Element("sampleAirTotTime: ", sampleAirTotTime);

			pXML->UpLevel();

			if (isCaseMaxMinPosZ){
				pXML->DownLevel("MaxMinPosZ");
			
					pXML->Element("MaxMinPosZx: ", MaxMinPosZ.x);
					pXML->Element("MaxMinPosZy: ", MaxMinPosZ.y);
					pXML->Element("MaxMinPosZz: ", MaxMinPosZ.z);

				pXML->UpLevel();

			}

			
			
			
		}
		pXML->DownLevel("Voxel Positions");
			int iT = NumVox();
			for (int i=0; i<iT; i++){
				pXML->Element("Voxel num: ", i);
				if (isSavePosition){
					pXML->Element("Voxel x: ", VoxArray[i].GetCurPos().x);
					pXML->Element("Voxel y: ", VoxArray[i].GetCurPos().y);
					pXML->Element("Voxel z: ", VoxArray[i].GetCurPos().z);
				}
				if(isSaveStrainEnergy){
					pXML->Element("Voxel StrainEnergy: ", VoxArray[i].GetMaxBondStrainE());
				}
				if(isSaveOrientation){
					Quat3D<double> orientation = VoxArray[i].GetCurAngle();

					// Vec3D<> orientation=VoxArray[i].GetCurAngle().ToRotationVector();
					pXML->Element("Voxel Angle: ", orientation.AngleDegrees());
					pXML->Element("Voxel Orientx: ", orientation.x);
					pXML->Element("Voxel Orienty: ", orientation.y);
					pXML->Element("Voxel Orientz: ", orientation.z);
				}
				if (isSaveVelocity){
					pXML->Element("Voxel Velx: ", VoxArray[i].GetCurVel().x);
					pXML->Element("Voxel Vely: ", VoxArray[i].GetCurVel().y);
					pXML->Element("Voxel Velz: ", VoxArray[i].GetCurVel().z);
				}
				if (isSaveAngVel){
					pXML->Element("Voxel AngVelx: ", VoxArray[i].GetCurAngVel().x);
					pXML->Element("Voxel AngVely: ", VoxArray[i].GetCurAngVel().y);
					pXML->Element("Voxel AngVelz: ", VoxArray[i].GetCurAngVel().z);
				}
				if(isSaveKineticEnergy){
					pXML->Element("Voxel KineticEnergy: ", VoxArray[i].GetCurKineticE());
				}
				if(isSavePressure){
					pXML->Element("Voxel Pressure: ", VoxArray[i].GetPressure());
				}
				if(isSaveForce){
					pXML->Element("Voxel Forcex: ", VoxArray[i].GetCurForce().x);
					pXML->Element("Voxel Forcey: ", VoxArray[i].GetCurForce().y);
					pXML->Element("Voxel Forcez: ", VoxArray[i].GetCurForce().z);
				}
				// if(isSaveMaxZPos){
				// 	pXML->Element("Voxel Forcex: ", VoxArray[i].GetCurForce().x);
				// 	pXML->Element("Voxel Forcey: ", VoxArray[i].GetCurForce().y);
				// 	pXML->Element("Voxel Forcez: ", VoxArray[i].GetCurForce().z);
				// }
			}
		pXML->UpLevel();
		


		// pXML->DownLevel("Fitness");
		//
		// 		pXML->Element("Beam End Final Position x:", VoxArray[0].GetCurPos().x);
		// 		pXML->Element("Beam End Final Position y:", VoxArray[0].GetCurPos().y);
		// 		pXML->Element("Beam End Final Position z:", VoxArray[0].GetCurPos().z);
			// pXML->Element("NormFinalDist", normFinalDist - normFrozenDist);
			// pXML->Element("NormRegimeDist", normRegimeDist);
			// pXML->Element("NormFrozenDist", normFrozenDist);
			//
			// pXML->Element("FinalDist", finalDist);
			// pXML->Element("finalDistY", finalDistY);
			//
			// pXML->Element("AnteriorDist", SS.CurAnteriorDist);
			// pXML->Element("PosteriorDist", SS.CurPosteriorDist);
			//
			// pXML->Element("AnteriorY", SS.CurAnteriorY);
			// pXML->Element("PosteriorY", SS.CurPosteriorY);
			//
			// pXML->Element("EndOfLifePosteriorY", SS.EndOfLifetimePosteriorY);
			//
			// pXML->Element("FallAdjPostY", FallAdjPostY);
			//
			// pXML->Element("NumNonFeetTouchingFloor", SS.CurNumNonFeetTouchingFloor);
			// pXML->Element("NumTouchingFloor", SS.CurNumTouchingFloor);
			//
			// pXML->Element("Lifetime", CurTime - AfterlifeTime);
			//
			// pXML->Element("FoundNeedleInHaystack", FoundNeedleInHaystack);
			// pXML->Element("PushDist", PushDist);

		// pXML->UpLevel();

		// if (pEnv->getTimeBetweenTraces() > 0 && pEnv->getUsingSaveTraces())
		// {
		// 	pXML->DownLevel("CMTrace");
		// 		for(std::vector<vfloat>::size_type i = 0; i != SS.CMTraceTime.size(); ++i)
		// 		{
	  //  				pXML->DownLevel("TraceStep");
	  //  					pXML->Element("Time",SS.CMTraceTime[i]);
		// 				pXML->Element("TraceX",SS.CMTrace[i].x);
		// 				pXML->Element("TraceY",SS.CMTrace[i].y);
		// 				pXML->Element("TraceZ",SS.CMTrace[i].z);
		// 			pXML->UpLevel();
		// 		}
		// 	pXML->UpLevel();
		// }
		//
		// if (pEnv->getUsingNormDistByVol() && pEnv->getUsingSaveTraces())
		// {
		// 	pXML->DownLevel("VolumeTrace");
		// 		for(std::vector<vfloat>::size_type i = 0; i != SS.VolTraceTime.size(); ++i)
		// 		{
	  //  				pXML->DownLevel("TraceStep");
	  //  					pXML->Element("Time",SS.VolTraceTime[i]);
		// 				pXML->Element("Volume",SS.VolTrace[i]);
		// 			pXML->UpLevel();
		// 		}
		// 	pXML->UpLevel();
		// }

	pXML->UpLevel();


}

void CVX_SimGA::WriteAdditionalSimXML(CXML_Rip* pXML)
{
	pXML->DownLevel("GA");
		pXML->Element("Fitness", Fitness);
		pXML->Element("FitnessType", (int)FitnessType);
		pXML->Element("TrackVoxel", TrackVoxel);
		pXML->Element("FitnessFileName", FitnessFileName);
		pXML->Element("WriteFitnessFile", WriteFitnessFile);
	pXML->UpLevel();
}

bool CVX_SimGA::ReadAdditionalSimXML(CXML_Rip* pXML, std::string* RetMessage)
{
	if (pXML->FindElement("GA")){
		int TmpInt;
		if (!pXML->FindLoadElement("Fitness", &Fitness)) Fitness = 0;
		if (pXML->FindLoadElement("FitnessType", &TmpInt)) FitnessType=(FitnessTypes)TmpInt; else Fitness = 0;
		if (!pXML->FindLoadElement("TrackVoxel", &TrackVoxel)) TrackVoxel = 0;
		if (!pXML->FindLoadElement("FitnessFileName", &FitnessFileName)) FitnessFileName = "";
		if (!pXML->FindLoadElement("QhullTmpFile", &QhullTmpFile)) QhullTmpFile = "";
		if (!pXML->FindLoadElement("CurvaturesTmpFile", &CurvaturesTmpFile)) CurvaturesTmpFile = "";
		if (!pXML->FindLoadElement("WriteFitnessFile", &WriteFitnessFile)) WriteFitnessFile = true;
		pXML->UpLevel();
	}

	return true;
}

// {
// 	int tmpInt;
// 	vfloat tmpVFloat;
// 	bool tmpBool;
//
//
// 	if (pXML->FindElement("Integration")){
// //		if (pXML->FindLoadElement("Integrator", &tmpInt)) CurIntegrator = (IntegrationType)tmpInt; else CurIntegrator = I_EULER;
// 		if (!pXML->FindLoadElement("DtFrac", &DtFrac)) DtFrac = (vfloat)0.9;
// 		pXML->UpLevel();
// 	}
//
// 	if (pXML->FindElement("Damping")){
// 		if (!pXML->FindLoadElement("BondDampingZ", &BondDampingZ)) BondDampingZ = 0.1;
// 		if (!pXML->FindLoadElement("ColDampingZ", &ColDampingZ)) ColDampingZ = 1.0;
// 		if (!pXML->FindLoadElement("SlowDampingZ", &SlowDampingZ)) SlowDampingZ = 1.0;
// 		pXML->UpLevel();
// 	}
//
// 	if (pXML->FindElement("Collisions")){
// 		if (!pXML->FindLoadElement("SelfColEnabled", &tmpBool)) tmpBool=false; EnableFeature(VXSFEAT_COLLISIONS, tmpBool);
// 		if (pXML->FindLoadElement("ColSystem", &tmpInt)) CurColSystem = (ColSystem)tmpInt; else CurColSystem = COL_SURFACE_HORIZON;
// 		if (!pXML->FindLoadElement("CollisionHorizon", &CollisionHorizon)) CollisionHorizon = (vfloat)2.0;
// 		pXML->UpLevel();
// 	}
//
// 	if (pXML->FindElement("Features")){
// 		if (!pXML->FindLoadElement("MaxVelLimitEnabled", &tmpBool)) tmpBool = false; EnableFeature(VXSFEAT_MAX_VELOCITY, tmpBool);
// 		if (!pXML->FindLoadElement("MaxVoxVelLimit", &MaxVoxVelLimit)) MaxVoxVelLimit = (vfloat)0.1;
// 		if (!pXML->FindLoadElement("BlendingEnabled", &tmpBool)) tmpBool = false; EnableFeature(VXSFEAT_BLENDING, tmpBool);
//
//
// 		if (pXML->FindLoadElement("MixRadius", &tmpVFloat)) MixRadius = Vec3D<>(tmpVFloat, tmpVFloat, tmpVFloat); //look for legacy first
// 		else {
// 			if (!pXML->FindLoadElement("XMixRadius", &MixRadius.x)) MixRadius.x = 0;
// 			if (!pXML->FindLoadElement("YMixRadius", &MixRadius.y)) MixRadius.y = 0;
// 			if (!pXML->FindLoadElement("ZMixRadius", &MixRadius.z)) MixRadius.z = 0;
// 		}
//
// 		if (pXML->FindLoadElement("BlendModel", &tmpInt)) BlendModel = (MatBlendModel)tmpInt; else BlendModel = MB_LINEAR;
// 		if (!pXML->FindLoadElement("PolyExp", &PolyExp)) PolyExp = 1.0;
//
// 		if (!pXML->FindLoadElement("FluidDampEnabled", &tmpBool)) tmpBool = false; //do nothing for now...
// 		if (!pXML->FindLoadElement("VolumeEffectsEnabled", &tmpBool)) tmpBool = false; EnableFeature(VXSFEAT_VOLUME_EFFECTS, tmpBool);
// 		if (!pXML->FindLoadElement("EnforceLatticeEnabled", &tmpBool)) tmpBool = false;  //do nothing for now...
// 		pXML->UpLevel();
// 	}
//
// 	if (pXML->FindElement("StopCondition")){
// 		if (pXML->FindLoadElement("StopConditionType", &tmpInt)) SetStopConditionType((StopCondition)tmpInt); else SetStopConditionType();
// 		if (pXML->FindLoadElement("StopConditionValue", &tmpVFloat)) SetStopConditionValue(tmpVFloat); else SetStopConditionValue();
// 		if (pXML->FindLoadElement("AfterlifeTime", &tmpVFloat)) SetAfterlifeTime(tmpVFloat); else SetAfterlifeTime();
// 		if (pXML->FindLoadElement("MidLifeFreezeTime", &tmpVFloat)) SetMidLifeFreezeTime(tmpVFloat); else SetMidLifeFreezeTime();
// 		if (pXML->FindLoadElement("InitCmTime", &tmpVFloat)) SetInitCmTime(tmpVFloat); else SetInitCmTime();
// 		pXML->UpLevel();
// 	}
//
// 	if (pXML->FindElement("EquilibriumMode")){
// 		if (!pXML->FindLoadElement("EquilibriumModeEnabled", &tmpBool)) tmpBool = false; if (tmpBool && !IsFeatureEnabled(VXSFEAT_EQUILIBRIUM_MODE)) EnableFeature(VXSFEAT_EQUILIBRIUM_MODE, true);
// 		//if (EquilibriumModeEnabled) EnableEquilibriumMode(true); //so it can set up energy history if necessary
// 		pXML->UpLevel();
// 	}
//
// //	MeshAutoGenerated=true;
// 	if (pXML->FindElement("SurfMesh")){
// 		if (pXML->FindElement("CMesh")){
// 			if (!ImportSurfMesh) ImportSurfMesh = new CMesh;
// 			//MeshAutoGenerated=false;
// 			ImportSurfMesh->ReadXML(pXML);
// 			pXML->UpLevel();
// 		}
// 		pXML->UpLevel();
// 	}
//
// 	if (!pXML->FindLoadElement("MinTempFact", &MIN_TEMP_FACT)) MIN_TEMP_FACT = 0.1;
// 	if (!pXML->FindLoadElement("MaxTempFactChange", &MAX_TEMP_FACT_VARIATION_STEP)) MAX_TEMP_FACT_VARIATION_STEP = 0.00015;
// 	if (!pXML->FindLoadElement("MaxStiffnessChange", &MAX_STIFFNESS_VARIATION_STEP)) MAX_STIFFNESS_VARIATION_STEP = 0.00015;
// 	if (!pXML->FindLoadElement("MinElasticMod", &MinElasticMod)) MinElasticMod = 5e006;
// 	if (!pXML->FindLoadElement("MaxElasticMod", &MaxElasticMod)) MaxElasticMod = 5e008;
//
// 	if (!pXML->FindLoadElement("MaxKP", &MaxKP)) MaxKP = 5;
// 	if (!pXML->FindLoadElement("MaxKI", &MaxKI)) MaxKI = 1;
// 	if (!pXML->FindLoadElement("MaxANTIWINDUP", &MaxANTIWINDUP)) MaxANTIWINDUP = 1;
//
// 	if (!pXML->FindLoadElement("ParentLifetime", &ParentLifetime)) ParentLifetime = GetStopConditionValue();
//
// 	if (!pXML->FindLoadElement("ErrorThreshold", &errorThreshold)) errorThreshold = 0.1;
// 	if (!pXML->FindLoadElement("ThresholdTime", &thresholdTime)) thresholdTime = 2.0;
//
// 	return ReadAdditionalSimXML(pXML, RetMessage);
// }
