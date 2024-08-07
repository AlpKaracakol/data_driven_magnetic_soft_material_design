/*******************************************************************************
Copyright (c) 2010, Jonathan Hiller (Cornell University)
If used in publication cite "J. Hiller and H. Lipson "Dynamic Simulation of Soft Heterogeneous Objects" In press. (2011)"

This file is part of Voxelyze.
Voxelyze is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Voxelyze is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
See <http://www.opensource.org/licenses/lgpl-3.0.html> for license details.
*******************************************************************************/

#include "VXS_Voxel.h"
#include "VXS_Bond.h"
#include "VX_Sim.h"
#include <algorithm> // std::max

CVXS_Voxel::CVXS_Voxel(CVX_Sim* pSimIn, int SIndexIn, int XIndexIn, int MatIndexIn, Vec3D<>& NominalPositionIn, vfloat OriginalScaleIn, bool trackThisVoxelIn) : CVX_Voxel(pSimIn, SIndexIn, XIndexIn, MatIndexIn, NominalPositionIn, OriginalScaleIn)
{
	trackThisVoxel = trackThisVoxelIn;
	//lastScale = initialVoxelSize; // -> nominal size
	ResetVoxel(); //sets state variables to zero

	// Magnetization properties
	M_DirecInit = Vec3D<>(0,0,0);
	M_DirecCur = Vec3D<>(0,0,0);
	M_Magnitude = 0.0;  // TODO: --> check here, could be done in material section later @alp
	m_MomentCur = Vec3D<>(0,0,0);
	M_PerVol = 0.0;

	F_Ext_Dist = Vec3D<>(0,0,0);

	M_PerVol = _pMat->GetMPerVol();
	M_Magnitude = M_PerVol*NominalSize*NominalSize*NominalSize;

	// external magnetic field
	B_Ext = Vec3D<>(0,0,0);
	Bgrad_Ext =  Vec3D<>(0,0,0);


	ExternalInputScale = 1.0;

//	CornerPosCur = Vec3D<>(OriginalScaleIn/2, OriginalScaleIn/2, OriginalScaleIn/2);
//	CornerNegCur = Vec3D<>(-OriginalScaleIn/2, -OriginalScaleIn/2, -OriginalScaleIn/2);

	SetColor(0,0,0,1);
	currentStimulus = 0.0;

	initialVoxPointingVector.setX(0.0);
	initialVoxPointingVector.setY(0.0);
	initialVoxPointingVector.setZ(0.0);

	voxPointingVector.setX(0.0);
	voxPointingVector.setY(0.0);
	voxPointingVector.setZ(0.0);

	targetPosition.setX(0.0);
	targetPosition.setY(0.0);
	targetPosition.setZ(0.0);

	desiredPointingVector.setX(0.0);
	desiredPointingVector.setY(0.0);
	desiredPointingVector.setZ(0.0);


	voxPointingError = 0.0;
	integralComponent = 0.0;
}

CVXS_Voxel::~CVXS_Voxel(void)
{
}

CVXS_Voxel& CVXS_Voxel::operator=(const CVXS_Voxel& VIn)
{
	CVX_Voxel::operator=(VIn);

	ExternalInputScale=VIn.ExternalInputScale;

	InputForce = Vec3D<>(0,0,0);

	Pos = VIn.Pos;
	LinMom = VIn.LinMom;
	Angle = VIn.Angle;
	AngMom = VIn.AngMom;
	Vel = VIn.Vel;
	KineticEnergy = VIn.KineticEnergy;
	AngVel = VIn.AngVel;
	Pressure = VIn.Pressure;
	Scale=VIn.Scale;

	StaticFricFlag = VIn.StaticFricFlag;
	VYielded = VIn.VYielded;
	VBroken = VIn.VBroken;

	ColBondInds = VIn.ColBondInds;
	UpdateColBondPointers();

	m_Red = VIn.m_Red;
	m_Green = VIn.m_Green;
	m_Blue = VIn.m_Blue;
	m_Trans = VIn.m_Trans;

//	SizeCurrent = VIn.SizeCurrent;
	CornerPosCur = VIn.CornerPosCur;
	CornerNegCur = VIn.CornerNegCur;

	ForceCurrent = VIn.ForceCurrent;

	// Magnetic properties
	M_DirecInit = VIn.M_DirecInit;
	M_DirecCur = VIn.M_DirecCur;
	M_Magnitude = VIn.M_Magnitude;  // TODO: --> check here, could be done in material section later @alp
	m_MomentCur = VIn.m_MomentCur;
	M_PerVol = VIn.M_PerVol;

	B_Ext = VIn.B_Ext;

	F_Ext_Dist = VIn.F_Ext_Dist;

	return *this;
}

void CVXS_Voxel::ResetVoxel(void) //resets this voxel to its defualt (imported) state.
{
	LinMom = Vec3D<double>(0,0,0);
	Angle = Quat3D<double>(1.0, 0, 0, 0);
	AngMom = Vec3D<double>(0,0,0);
	Scale = 0;
	Vel = Vec3D<>(0,0,0);
	KineticEnergy = 0;
	AngVel = Vec3D<>(0,0,0);
	Pressure=0;
	currentStimulus = 0.0;

	Pos = GetNominalPosition(); //only position and size need to be set

	Scale = GetNominalSize(); // initialVoxelSize
	lastScale = Scale;

	//lastTempFact = Scale/GetNominalSize();
	// TempFact = ?

	InputForce = Vec3D<>(0,0,0); //?


	StaticFricFlag = false;
	VYielded = false;
	VBroken = false;

//	SizeCurrent = Vec3D<>(Scale, Scale, Scale);
	CornerPosCur = Vec3D<>(Scale/2, Scale/2, Scale/2);
	CornerNegCur = Vec3D<>(-Scale/2, -Scale/2, -Scale/2);
//	CornerPosCur = Vec3D<>(0,0,0);
//	CornerNegCur = Vec3D<>(0,0,0);
	ForceCurrent = Vec3D<>(0,0,0);
	StrainPosDirsCur = Vec3D<>(0,0,0);
	StrainNegDirsCur = Vec3D<>(0,0,0);
	integralComponent = 0;
	currentStimulus = 0;

	//lastTempFact = 1;
}


bool CVXS_Voxel::LinkColBond(int CBondIndex) //simulation bond index...
{
	if (!pSim || CBondIndex >= pSim->BondArrayCollision.size()) return false;

	ColBondInds.push_back(CBondIndex);
	ColBondPointers.push_back(&(pSim->BondArrayCollision[CBondIndex]));

	return true;
}

void CVXS_Voxel::UnlinkColBonds(void)
{
	ColBondInds.clear();
	ColBondPointers.clear();
}


void CVXS_Voxel::UpdateColBondPointers() //updates all links (pointers) to bonds according top current p_Sim
{
	int NumColBonds = ColBondInds.size();
	if (NumColBonds == 0) return;
	ColBondPointers.resize(NumColBonds);
	for (int i=0; i<NumColBonds; i++){
		ColBondPointers[i] = &(pSim->BondArrayCollision[ColBondInds[i]]);
	}
}


//http://klas-physics.googlecode.com/svn/trunk/src/general/Integrator.cpp (reference)
void CVXS_Voxel::EulerStep()
{
	double dt = pSim->dt;

	//bool EqMode = p_Sim->IsEquilibriumEnabled();
	if (IS_ALL_FIXED(DofFixed) & !pSim->IsFeatureEnabled(VXSFEAT_VOLUME_EFFECTS)){ //if fixed, just update the position and forces acting on it (for correct simulation-wide summing
		LinMom = Vec3D<double>(0,0,0);
		Pos = NominalPosition + ExternalInputScale*ExternalDisp;
		AngMom = Vec3D<double>(0,0,0);
		Angle.FromRotationVector(Vec3D<double>(ExternalInputScale*ExternalTDisp));
	}
	else {
		Vec3D<> ForceTot = CalcTotalForce(); //TotVoxForce;

		//DISPLACEMENT
		LinMom = LinMom + ForceTot*dt;
		Vec3D<double> Disp(LinMom*(dt*_massInv)); //vector of what the voxel moves

//		if(pSim->IsMaxVelLimitEnabled()){ //check to make sure we're not going over the speed limit!
		if(pSim->IsFeatureEnabled(VXSFEAT_MAX_VELOCITY)){ //check to make sure we're not going over the speed limit!
			vfloat DispMag = Disp.Length();
			vfloat MaxDisp = pSim->GetMaxVoxVelLimit()*NominalSize; // p_Sim->pEnv->pObj->GetLatticeDim();
			if (DispMag>MaxDisp) Disp *= (MaxDisp/DispMag);
		}
		Pos += Disp; //update position (source of noise in float mode???

		if (IS_FIXED(DOF_X, DofFixed)){Pos.x = NominalPosition.x + ExternalInputScale*ExternalDisp.x; LinMom.x = 0;}
		if (IS_FIXED(DOF_Y, DofFixed)){Pos.y = NominalPosition.y + ExternalInputScale*ExternalDisp.y; LinMom.y = 0;}
		if (IS_FIXED(DOF_Z, DofFixed)){Pos.z = NominalPosition.z + ExternalInputScale*ExternalDisp.z; LinMom.z = 0;}

		//ANGLE
		Vec3D<> TotVoxMoment = CalcTotalMoment(); //debug

		AngMom = AngMom + TotVoxMoment*dt;

		if (pSim->IsFeatureEnabled(VXSFEAT_VOLUME_EFFECTS)) AngMom /= 1.01; //TODO: remove angmom altogehter???
		else {
			vfloat AngMomFact = (1 - 10*pSim->GetSlowDampZ() * _inertiaInv *_2xSqIxExSxSxS*dt);
			AngMom *= AngMomFact;
		}

		//convert Angular velocity to quaternion form ("Spin")
		Vec3D<double> dSAngVel(AngMom * _inertiaInv);
		Quat3D<double> Spin = 0.5 * Quat3D<double>(0, dSAngVel.x, dSAngVel.y, dSAngVel.z) * Angle; //current "angular velocity"

		Angle += Quat3D<double>(Spin*dt); //see above
		Angle.NormalizeFast(); //Through profiling, quicker to normalize every time than check to see if needed then do it...

	//	TODO: Only constrain fixed angles if one is non-zero! (support symmetry boundary conditions while still only doing this calculation) (only works if all angles are constrained for now...)
		if (IS_FIXED(DOF_TX, DofFixed) && IS_FIXED(DOF_TY, DofFixed) && IS_FIXED(DOF_TZ, DofFixed)){
			Angle.FromRotationVector(Vec3D<double>(ExternalInputScale*ExternalTDisp));
			AngMom = Vec3D<>(0,0,0);
		}
	}

	// SCALE
	vfloat maxScale = (1+pSim->pEnv->getGrowthAmplitude())*GetNominalSize();  // max size is specified by growth amplitude
    vfloat minScale = pSim->getMinTempFact()*GetNominalSize();  // min size has hard limit based on physics engine stability
    vfloat currScale = Scale;
    vfloat CtrlTempFact = 0;
    vfloat DevTempFact = 0;
    vfloat DevPhaseAddOn = 0;
    vfloat DevTempAmpDampAddOn = 0;
    vfloat k = 0;
    vfloat FrozenTimeAdj = 0;
    vfloat FreezeInitialized = 1;

    // Prenatal linear development - occurs before actuation (very large, quick changes in scale can cause instability)
    vfloat c = (pSim->CurTime >= 0.5 * pSim->GetInitCmTime()) ? 1.0 : 2*pSim->CurTime/pSim->GetInitCmTime();
    vfloat PreNatalTempFrac = c * ((initialVoxelSize / GetNominalSize()) - 1);


    // Freeze development in the middle of the lifetime
    if (pSim->GetMidLifeFreezeTime() > 0)
    {
        vfloat middleTime = 0.5 * (pSim->GetStopConditionValue() - pSim->GetInitCmTime());
        vfloat FreezeStart = middleTime - 0.5*pSim->GetMidLifeFreezeTime();
        vfloat FreezeEnd = middleTime + 0.5*pSim->GetMidLifeFreezeTime();

        if ((pSim->CurTime > FreezeStart) and (pSim->CurTime < FreezeEnd))
        {
            FrozenTimeAdj = pSim->CurTime - FreezeStart;
            if (pSim->CurTime < FreezeStart + pSim->GetInitCmTime())
            {
                FreezeInitialized = 0;
            }
        }
        if (pSim->CurTime > FreezeEnd)
        {
            FrozenTimeAdj = pSim->GetMidLifeFreezeTime();
        }
    }

	// Postnatal linear development
    if ((pSim->CurTime >= startGrowthTime) && (growthTime>0))
	{
        vfloat EffectiveCurTime = (pSim->CurTime <=  startGrowthTime + growthTime + pSim->GetMidLifeFreezeTime()) ? pSim->CurTime : startGrowthTime + growthTime + pSim->GetMidLifeFreezeTime();
        // when EffectiveCurTime = StartGrowthTime: k=0, when the EffectiveCurTime = startGrowthTime+growthTime: k=1
        EffectiveCurTime = EffectiveCurTime - FrozenTimeAdj;
        k = (EffectiveCurTime - startGrowthTime) / growthTime;

        if (pSim->pEnv->pObj->GetUsingFinalVoxelSize())
        {
		    DevTempFact = k * ((finalVoxelSize / initialVoxelSize) - 1.0);  // need to get a TempFact from a voxel size
		}

		// for now we only have a single growthTime for control and morphology
		if (pSim->pEnv->pObj->GetUsingFinalPhaseOffset())
        {
		    DevPhaseAddOn = k * (finalPhaseOffset - phaseOffset);
		    // std::cout << "k: " << k  << std::endl;
		    // std::cout << "init: " << phaseOffset  << std::endl;
		    // std::cout << "final: " << finalPhaseOffset  << std::endl;
		}

		if (pSim->pEnv->pObj->GetUsingFinalTempAmpDamp())
        {
		    DevTempAmpDampAddOn = k * (finalTempAmpDamp - TempAmpDamp);
		}

    }

    // Control - thermal actuation
	if (pSim->IsFeatureEnabled(VXSFEAT_TEMPERATURE) and pSim->CurTime >= pSim->GetInitCmTime())
	{
		vfloat ThisTemp = _pMat->GetCurMatTemp();
		vfloat ThisCTE = GetCTE();
		vfloat TempBase =  pSim->pEnv->GetTempBase();

	    vfloat ThisPhase = phaseOffset + DevPhaseAddOn;
	    // std::cout << "phase: " << ThisPhase  << std::endl;
	    vfloat ThisTempAmpDamp = TempAmpDamp + DevTempAmpDampAddOn;
	    // std::cout << "Temp Amp Damping: " << ThisTempAmpDamp  << std::endl;
		CtrlTempFact = ThisTempAmpDamp*(TempAmplitude*sin(2*3.1415926f * (pSim->CurTime/TempPeriod + ThisPhase)))*ThisCTE*FreezeInitialized;
		//std::cout << "CtrlTempFact: " << CtrlTempFact  << std::endl;
		//std::cout << "ThisCTE: " << ThisCTE  << std::endl;
	}

    // Adjust actuation relative to size
    if (pSim->pEnv->pObj->GetUsingInitialVoxelSize() || pSim->pEnv->pObj->GetUsingFinalVoxelSize())
    {
        // calc size based on pre and post natal growth/shrinkage
        vfloat currSize = (1+PreNatalTempFrac)*(1+DevTempFact)*GetNominalSize();

        // back out from size to the original sigmoid (but is truncated below minTempFact in Sim.cpp)
        vfloat originalSigmoid = (currSize/GetNominalSize()-1) / pSim->pEnv->getGrowthAmplitude();
        vfloat positiveSigmoid = (originalSigmoid + 1) * 0.5;  // smush it from (-1, 1) to (0, 1)
        vfloat cappedSigmoid = (positiveSigmoid > 0.5) ? 0.5 : positiveSigmoid;  // limit the actuation for shrinking voxels

        // apply limits to actuation
        CtrlTempFact = CtrlTempFact*cappedSigmoid*2;
    }

    // scale with actuation based on current size
    currScale = CtrlTempFact*GetNominalSize() + (1+PreNatalTempFrac)*(1+DevTempFact)*GetNominalSize();

    // apply limits to scale
	if (currScale < lastScale && currScale < minScale) {
	    currScale = lastScale;
	}

	if (currScale > lastScale && currScale > maxScale) {
	    currScale = lastScale;
	}

    // finally set new scale of voxel based on pre and post natal development as well as limited actuation
	Scale = currScale;
	lastScale = Scale;

    // used for coloring
    RemainingGrowth = finalVoxelSize - (1+PreNatalTempFrac)*(1+DevTempFact)*GetNominalSize();
    CurPhaseChange = phaseOffset + DevPhaseAddOn;

	// Velocity adjusted development
	double GrowthBuffer = pSim->pEnv->getMinGrowthTime();  // should this be smaller?
    if ((pSim->pEnv->GetNumTimeStepsInWindow() > 0) and (pSim->CurTime >= startGrowthTime + GrowthBuffer))
    {
        int TimeInWindow = pSim->pEnv->GetNumTimeStepsInWindow()*pSim->pEnv->getTimeBetweenTraces();
        int NumWindows = pSim->SS.WindowTrace.size();
        if (pSim->CurTime >= pSim->GetInitCmTime() + 2*TimeInWindow)  // wait until two full windows calculated (two actuation cycles)
        {
            double thisSpeed = pSim->SS.WindowTrace[NumWindows];
            double lastSpeed = pSim->SS.WindowTrace[NumWindows-1];
            double IsSpeedDecreasing = 0;
            //std::cout << "ratio speed: " << thisSpeed/lastSpeed <<std::endl;
            if ((lastSpeed>0) and (thisSpeed < lastSpeed))
            {
                IsSpeedDecreasing = (thisSpeed/lastSpeed < 1-pSim->pEnv->GetMaxSlowdownPermitted()) ? 1 : 0;
            }
            double BallisticSpeedAdjustment = 1 - IsSpeedDecreasing * pSim->pEnv->GetBallisticSlowdownFact();
            // when speed is not decreasing there is no adjustment (keep developing)
            // otherwise apply slowdown factor (can be evolved)
            // once BallisticSpeedAdjustment is zero development stops indefinitely

            initialVoxelSize = (1+PreNatalTempFrac)*(1+DevTempFact)*GetNominalSize();
            SuggestedFinalVoxelSize = initialVoxelSize + (finalVoxelSize-initialVoxelSize)*BallisticSpeedAdjustment;
            //std::cout << "delta devo: " << finalVoxelSize/OriginalFinalVoxelSize-1 <<std::endl;

            // ensure monotonicity and original bounds
            if (OriginalFinalVoxelSize > initialVoxelSize) {
                SuggestedFinalVoxelSize = (SuggestedFinalVoxelSize > OriginalFinalVoxelSize) ? OriginalFinalVoxelSize : SuggestedFinalVoxelSize;
                finalVoxelSize = (SuggestedFinalVoxelSize >= initialVoxelSize) ? SuggestedFinalVoxelSize : initialVoxelSize;
            }
            else {
                SuggestedFinalVoxelSize = (SuggestedFinalVoxelSize < OriginalFinalVoxelSize) ? OriginalFinalVoxelSize : SuggestedFinalVoxelSize;
                finalVoxelSize = (SuggestedFinalVoxelSize <= initialVoxelSize) ? SuggestedFinalVoxelSize : initialVoxelSize;
            }

            growthTime = growthTime - (pSim->CurTime - startGrowthTime);
            growthTime = (growthTime <= 0) ? 0 : growthTime;  // or should the bound be pSim->pEnv->getMinGrowthTime() ?
            startGrowthTime = pSim->CurTime;
        }
    }


//  vfloat TempFact = 0;
//  if (TempFact < pSim->getMinTempFact()) TempFact = pSim->getMinTempFact();

//	if (pSim->CurTime >= pSim->GetInitCmTime())
//	{
//		// saturation of voxel size
//		if (pSim->pEnv->pObj->GetUsingFinalVoxelSize() || pSim->pEnv->pObj->GetUsingGrowthTime())
//		{
//			if (TempFact >= (1 + pSim->pEnv->getGrowthAmplitude()) && TempFact > lastTempFact)
//			{
//			    // we've reached the maximum/minimum dimension, stop growth
//				TempFact = lastTempFact;
//			}
//		}
//
//		// FC: This, instead, should always be ensured (I believe)
//		if (TempFact  <= pSim->getMinTempFact() && TempFact < lastTempFact)
//		{
//			// we've reached the maximum/minimum dimension, stop growth
//			TempFact = lastTempFact;
//		}
//	}

//      //  New size of the voxel
//      Scale = TempFact*GetNominalSize();

//      lastTempFact = TempFact;


	//Recalculate secondary:
	AngVel = AngMom * _inertiaInv;
	Vel = LinMom * _massInv;
	if(pSim->StatToCalc & CALCSTAT_KINE) KineticEnergy = 0.5*Mass*Vel.Length2() + 0.5*Inertia*AngVel.Length2(); //1/2 m v^2

	if(pSim->StatToCalc & CALCSTAT_PRESSURE)
	{
		//vfloat VolumetricStrain = StrainPosDirsCur.x/2 + StrainPosDirsCur.y/2 + StrainPosDirsCur.z/2 + StrainNegDirsCur.x/2 + StrainNegDirsCur.y/2 + StrainNegDirsCur.z/2;
		vfloat VolumetricStrain = GetVoxelStrain(AXIS_X) + GetVoxelStrain(AXIS_Y) + GetVoxelStrain(AXIS_Z);
		Pressure = - Vox_E*VolumetricStrain/(3*(1-2*_pMat->GetPoissonsRatio())); //http://www.colorado.edu/engineering/CAS/courses.d/Structures.d/IAST.Lect05.d/IAST.Lect05.pdf
	}

	// Vox_E is accessible here.
	firstStep = 0;
}


void CVXS_Voxel::SetColor(float r, float g, float b, float a)
{
	m_Red = r;
	m_Green = g;
	m_Blue = b;
	m_Trans = a;
}

void CVXS_Voxel::SetStrainDir(BondDir Bond, vfloat StrainIn)
{
	switch (Bond){
	case BD_PX: StrainPosDirsCur.x = StrainIn; break;
	case BD_PY: StrainPosDirsCur.y = StrainIn; break;
	case BD_PZ: StrainPosDirsCur.z = StrainIn; break;
	case BD_NX: StrainNegDirsCur.x = StrainIn; break;
	case BD_NY: StrainNegDirsCur.y = StrainIn; break;
	case BD_NZ: StrainNegDirsCur.z = StrainIn; break;
	}
}

vfloat CVXS_Voxel::GetVoxelStrain(Axis DesiredAxis)
{
	bool pd, nd; //positive and negative directions
	switch (DesiredAxis){
		case AXIS_X:
			pd = InternalBondPointers[BD_PX]!=NULL, nd = InternalBondPointers[BD_NX]!=NULL;
			if (!pd && !nd) return 0;
			else if (pd && !nd) return StrainPosDirsCur.x;
			else if (!pd && nd) return StrainNegDirsCur.x;
			else return 0.5*(StrainPosDirsCur.x + StrainNegDirsCur.x);
			break;
		case AXIS_Y:
			pd = InternalBondPointers[BD_PY]!=NULL, nd = InternalBondPointers[BD_NY]!=NULL;
			if (!pd && !nd) return 0;
			else if (pd && !nd) return StrainPosDirsCur.y;
			else if (!pd && nd) return StrainNegDirsCur.y;
			else return 0.5*(StrainPosDirsCur.y + StrainNegDirsCur.y);
			break;
		case AXIS_Z:
			pd = InternalBondPointers[BD_PZ]!=NULL, nd = InternalBondPointers[BD_NZ]!=NULL;
			if (!pd && !nd) return 0;
			else if (pd && !nd) return StrainPosDirsCur.z;
			else if (!pd && nd) return StrainNegDirsCur.z;
			else return 0.5*(StrainPosDirsCur.z + StrainNegDirsCur.z);
			break;
		default: return 0;

	}


}

Vec3D<> CVXS_Voxel::CalcTotalForce()
{
//	THE NEXT optimization target
	//INTERNAL forces
	Vec3D<> TotalForce = Vec3D<>(0,0,0);
	TotalForce += -pSim->GetSlowDampZ() * Vel*_2xSqMxExS; //(2*sqrt(Mass*GetEMod()*Scale.x));

	//POSSIONS!
//	Vec3D<> pStrain = Vec3D<>(0,0,0), nStrain = Vec3D<>(0,0,0),
	Vec3D<> CurLocStrain = Vec3D<>(0,0,0);
	//End Poissons


	//Forces from permanent bonds:
	for (int i=0; i<6; i++){
		CVXS_Bond* pThisBond = InternalBondPointers[i];
		if (!pThisBond) continue;

		if (IAmInternalVox2(i)) TotalForce += pThisBond->GetForce2();
		else TotalForce += pThisBond->GetForce1();


		//if (pSim->IsFeatureEnabled(VXSFEAT_VOLUME_EFFECTS)){
		//	bool IAmVox1 = !IAmInternalVox2(i);
		//	switch (pThisBond->GetBondAxis()){
		//		case AXIS_X: IAmVox1 ? pStrain.x = pThisBond->GetStrainV1() : nStrain.x = pThisBond->GetStrainV2(); break;
		//		case AXIS_Y: IAmVox1 ? pStrain.y = pThisBond->GetStrainV1() : nStrain.y = pThisBond->GetStrainV2(); break;
		//		case AXIS_Z: IAmVox1 ? pStrain.z = pThisBond->GetStrainV1() : nStrain.z = pThisBond->GetStrainV2(); break;
		//	}
		//}

	}

	//Forces from collision bonds: To optimize!
	if (pSim->IsFeatureEnabled(VXSFEAT_COLLISIONS)){
		int NumColBond = ColBondPointers.size();
		for (int i=0; i<NumColBond; i++){
			if (IAmVox2Col(i)) TotalForce += ColBondPointers[i]->GetForce2();
			else TotalForce += ColBondPointers[i]->GetForce1();

//			CVXS_Bond* pThisBond = ColBondPointers[i];
//			bool IAmVox1 = !IAmVox2Col(i); //IsMe(pThisBond->GetpV1()); //otherwise vox 2 of the bond

//			if (IAmVox1) TotalForce -= pThisBond->GetForce1(); //Force on Vox 1 from this bond
//			else TotalForce -= pThisBond->GetForce2(); //Force on Vox 2 from this bond
		}
	}

	//Forced from input bond
	TotalForce -= InputForce;



	//From gravity
	if (pSim->IsFeatureEnabled(VXSFEAT_GRAVITY))
		TotalForce.z += Mass*pSim->pEnv->GetGravityAccel();

	//EXTERNAL forces
	TotalForce += ExternalInputScale*ExternalForce; //add in any external forces....


	if (pSim->IsFeatureEnabled(VXSFEAT_VOLUME_EFFECTS)){
		//http://www.colorado.edu/engineering/CAS/courses.d/Structures.d/IAST.Lect05.d/IAST.Lect05.pdf

		vfloat mu = GetPoisson();

		bool px = (InternalBondPointers[BD_PX] != NULL);
		bool nx = (InternalBondPointers[BD_NX] != NULL);
		bool py = (InternalBondPointers[BD_PY] != NULL);
		bool ny = (InternalBondPointers[BD_NY] != NULL);
		bool pz = (InternalBondPointers[BD_PZ] != NULL);
		bool nz = (InternalBondPointers[BD_NZ] != NULL);

		bool Tx = px && nx || ((px || nx) && (IS_FIXED(DOF_X, DofFixed) || ExternalForce.x != 0)); //if bond on both sides or pulling against a fixed or forced constraint
		bool Ty = py && ny || ((py || ny) && (IS_FIXED(DOF_Y, DofFixed) || ExternalForce.y != 0)); //if bond on both sides or pulling against a fixed or forced constraint
		bool Tz = pz && nz || ((pz || nz) && (IS_FIXED(DOF_Z, DofFixed) || ExternalForce.z != 0)); //if bond on both sides or pulling against a fixed or forced constraint
		if (Tx){
			CurLocStrain.x = GetVoxelStrain(AXIS_X);
//			if (px && !nx) CurLocStrain.x = StrainPosDirsCur.x;
//			else if (!px && nx) CurLocStrain.x = StrainNegDirsCur.x;
//			else CurLocStrain.x = 0.5*(StrainPosDirsCur.x + StrainNegDirsCur.x);
		}
		if (Ty){
			CurLocStrain.y = GetVoxelStrain(AXIS_Y);

//			if (py && !ny) CurLocStrain.y = StrainPosDirsCur.y;
//			else if (!py && ny) CurLocStrain.y = StrainNegDirsCur.y;
//			else CurLocStrain.y = 0.5*(StrainPosDirsCur.y + StrainNegDirsCur.y);
		}
		if (Tz){
			CurLocStrain.z = GetVoxelStrain(AXIS_Z);

//			if (pz && !nz) CurLocStrain.z = StrainPosDirsCur.z;
//			else if (!pz && nz) CurLocStrain.z = StrainNegDirsCur.z;
//			else CurLocStrain.z = 0.5*(StrainPosDirsCur.z + StrainNegDirsCur.z);
		}


		if (!Tx && !Ty && !Tz) CurLocStrain = Vec3D<>(0,0,0); //if nothing pushing or pulling, no strain on this bond!
		//else if (!Tx && Ty && Tz) CurLocStrain.x = pow(1+CurLocStrain.y, -mu)-1 + pow(1+CurLocStrain.z, -mu)-1;
		//else if (Tx && !Ty && Tz) CurLocStrain.y = pow(1+CurLocStrain.x, -mu)-1 + pow(1+CurLocStrain.z, -mu)-1;
		//else if (Tx && Ty && !Tz) CurLocStrain.z = pow(1+CurLocStrain.x, -mu)-1 + pow(1+CurLocStrain.y, -mu)-1;
		else if (!Tx && Ty && Tz) CurLocStrain.x = pow(1+CurLocStrain.y + CurLocStrain.z, -mu)-1;
		else if (Tx && !Ty && Tz) CurLocStrain.y = pow(1+CurLocStrain.x + CurLocStrain.z, -mu)-1; //??
		else if (Tx && Ty && !Tz) CurLocStrain.z = pow(1+CurLocStrain.x + CurLocStrain.y, -mu)-1;
		else if (!Tx && !Ty && Tz) CurLocStrain.x = CurLocStrain.y = pow(1+CurLocStrain.z, -mu)-1;
		else if (!Tx && Ty && !Tz) CurLocStrain.x = CurLocStrain.z = pow(1+CurLocStrain.y, -mu)-1;
		else if (Tx && !Ty && !Tz) CurLocStrain.y = CurLocStrain.z = pow(1+CurLocStrain.x, -mu)-1;
		//else if (Tx && Ty && Tz) //we already have everything!

//		SizeCurrent.x = (1+CurLocStrain.x)*NominalSize;
//		SizeCurrent.y = (1+CurLocStrain.y)*NominalSize;
//		SizeCurrent.z = (1+CurLocStrain.z)*NominalSize;


		//TODO: get down to a force for this bond, then dump it (and current stiffness) to the bond
//		for (int i=0; i<NumLocBond; i++){
		for (int i=0; i<6; i++){
//			CVXS_Bond* pThisBond = GetBond(i);
			CVXS_Bond* pThisBond = InternalBondPointers[i];
			if (!pThisBond) continue;

			bool IAmVox1 = !IAmInternalVox2(i); //IsMe(pThisBond->GetpV1()); //otherwise vox 2 of the bond
			switch (pThisBond->GetBondAxis()){
			case AXIS_X:
				if (IAmVox1) {pThisBond->TStrainSum1 = CurLocStrain.y + CurLocStrain.z; pThisBond->CSArea1 = (1+CurLocStrain.y)*(1+CurLocStrain.z)*NominalSize*NominalSize;}
				else {pThisBond->TStrainSum2 = CurLocStrain.y + CurLocStrain.z; pThisBond->CSArea2 = (1+CurLocStrain.y)*(1+CurLocStrain.z)*NominalSize*NominalSize;}
				break;
			case AXIS_Y:
				if (IAmVox1) {pThisBond->TStrainSum1 = CurLocStrain.x + CurLocStrain.z; pThisBond->CSArea1 = (1+CurLocStrain.x)*(1+CurLocStrain.z)*NominalSize*NominalSize;}
				else {pThisBond->TStrainSum2 = CurLocStrain.x + CurLocStrain.z; pThisBond->CSArea2 = (1+CurLocStrain.x)*(1+CurLocStrain.z)*NominalSize*NominalSize;}
				break;
			case AXIS_Z:
				if (IAmVox1) {pThisBond->TStrainSum1 = CurLocStrain.y + CurLocStrain.x;  pThisBond->CSArea1 = (1+CurLocStrain.y)*(1+CurLocStrain.x)*NominalSize*NominalSize;}
				else {pThisBond->TStrainSum2 = CurLocStrain.y + CurLocStrain.x;  pThisBond->CSArea2 = (1+CurLocStrain.y)*(1+CurLocStrain.x)*NominalSize*NominalSize;}
				break;
			}
		}
	}
	else { //volume effects off
//		SizeCurrent = Vec3D<>(NominalSize, NominalSize, NominalSize);
		//for (int i=0; i<NumLocBond; i++){
		//	CVXS_Bond* pThisBond = GetBond(i);
		for (int i=0; i<6; i++){ //update for collision bonds?
			CVXS_Bond* pThisBond = InternalBondPointers[i];
			if (pThisBond){
				pThisBond->CSArea1 = pThisBond->CSArea2 = NominalSize*NominalSize;
				//pThisBond->CSArea2 = NominalSize*NominalSize;
			}
		}
	}

//	if(pSim->pEnv->IsFloorEnabled()){
	if(pSim->IsFeatureEnabled(VXSFEAT_FLOOR)){
		TotalForce += CalcFloorEffect(Vec3D<vfloat>(TotalForce));
		//else StaticFricFlag = false;
		if (StaticFricFlag) {TotalForce.x = 0; TotalForce.y = 0;} //no lateral movement if static friction in effect
	}

	CornerPosCur = (Vec3D<>(1,1,1)+StrainPosDirsCur)*NominalSize/2;
	CornerNegCur = -(Vec3D<>(1,1,1)+StrainNegDirsCur)*NominalSize/2;

	//Enforce fixed degrees of freedom (put no force on them so they don't move)
//	if (IS_FIXED(DOF_X, DofFixed) && WithRestraint) TotalForce.x=0;
//	if (IS_FIXED(DOF_Y, DofFixed) && WithRestraint) TotalForce.y=0;
//	if (IS_FIXED(DOF_Z, DofFixed) && WithRestraint) TotalForce.z=0;

	ForceCurrent=TotalForce;
	return ForceCurrent;
}

Vec3D<> CVXS_Voxel::CalcTotalMoment(void)
{
	Vec3D<> TotalMoment(0,0,0);
//	for (int i=0; i<GetNumLocalBonds(); i++) {
	//permanent bonds
	for (int i=0; i<6; i++){ //update for collision bonds?
		CVXS_Bond* pThisBond = InternalBondPointers[i];
		if (pThisBond){
			if (IAmInternalVox2(i)){ TotalMoment -= InternalBondPointers[i]->GetMoment2(); } //if this is voxel 2		//add moments from bond
			else { TotalMoment -= InternalBondPointers[i]->GetMoment1(); } //if this is voxel 1
		}
	}

	//EXTERNAL moments
////////////
/////////////
//////////////////////////////////////////////////////
/////////////
////////////
// Check here why commented out?

	TotalMoment += -pSim->GetSlowDampZ() * AngVel *_2xSqIxExSxSxS;
	TotalMoment += ExternalInputScale*ExternalTorque; //add in any external forces....

	if (IS_FIXED(DOF_TX, DofFixed)) TotalMoment.x=0;
	if (IS_FIXED(DOF_TY, DofFixed)) TotalMoment.y=0;
	if (IS_FIXED(DOF_TZ, DofFixed)) TotalMoment.z=0;

	////////////
	/////////////
	//////////////////////////////////////////////////////
	/////////////
	////////////


	return TotalMoment;
}

vfloat CVXS_Voxel::GetCurGroundPenetration() //how far into the ground penetrating (penetration is positive, no penetration is zero)
{

		//bool insideLimitedFloor = (Pos.x <= pSim->pEnv->getFloorSizeX() && Pos.x >= 0 && Pos.y <= pSim->pEnv->getFloorSizeY() && Pos.y >=0 && Pos.z >= pSim->pEnv->getFloorSizeZ() && Pos.z >= 0 ); // remove Pos.z >= 0  if you want to apply a force to voxels that re-enter the floor area from below. This can cause weird phenomena

		vfloat latDim = pSim->LocalVXC.GetLatticeDim();
		vfloat xDim = (vfloat)pSim->LocalVXC.GetVXDim();
		vfloat yDim = (vfloat)pSim->LocalVXC.GetVYDim();
//		vfloat zDim = (vfloat)pSim->LocalVXC.GetVZDim();

		Vec3D<> workspaceCenter(latDim*xDim*0.5, latDim*yDim*0.5, 0.0);
		Vec3D<> voxelProjectedPos(Pos.x, Pos.y, 0.0);
		vfloat distanceFromCenter = (voxelProjectedPos-workspaceCenter).Length();

		bool insideLimitedFloor = (distanceFromCenter <= pSim->pEnv->getFloorRadius() && Pos.z >= 0); // Circular floor

		if((pSim->pEnv->isFloorLimited() && insideLimitedFloor) || !pSim->pEnv->isFloorLimited())
		{
			vfloat Penetration = 0.5*Scale - Pos.z;
			return Penetration <= 0 ? 0 : Penetration;
		}

		return 0;
}

inline bool CVXS_Voxel::IAmVox2Col(const int BondDirColIndex) const
{
	return (this == ColBondPointers[BondDirColIndex]->GetpV2());
} //returns true if this voxel is Vox2 of the specified bond


Vec3D<> CVXS_Voxel::CalcFloorEffect(Vec3D<> TotalVoxForce) //calculates the object's interaction with a floor. should be calculated AFTER all other forces for static friction to work right...
{
	Vec3D<> FloorForce(0,0,0); //the force added by floor interactions...

	StaticFricFlag = false; //assume not under static friction unless we decide otherwise
	vfloat CurPenetration = GetCurGroundPenetration();


	if (CurPenetration>0){
		vfloat LocA1 = GetLinearStiffness(); //p_Sim->LocalVXC.GetBaseMat(MatIndex)->GetElasticMod()*2*NominalSize;
		vfloat LocUDynamic = _pMat->GetuDynamic();
		vfloat LocUStatic = _pMat->GetuStatic();

		vfloat NormalForce = LocA1 * CurPenetration; //positive for penetration...
		FloorForce.z += NormalForce; //force resisting penetration

		//do vertical damping here...
		FloorForce.z -= pSim->GetCollisionDampZ()*_2xSqMxExS*Vel.z;  //critically damp force for this bond to ground
//		FloorForce.z -= p_Sim->GetCollisionDampZ()*2*Mass*sqrt(LocA1/Mass)*Vel.z;  //critically damp force for this bond to ground

		//lateral friction
		vfloat SurfaceVel = sqrt(Vel.x*Vel.x + Vel.y*Vel.y); //velocity along the floor...
		vfloat SurfaceVelAngle = atan2(Vel.y, Vel.x); //angle of sliding along floor...
		vfloat SurfaceForce = sqrt(TotalVoxForce.x*TotalVoxForce.x + TotalVoxForce.y*TotalVoxForce.y);
		vfloat dFrictionForce = LocUDynamic*NormalForce;
		Vec3D<> FricForceToAdd = -Vec3D<>(cos(SurfaceVelAngle)*dFrictionForce, sin(SurfaceVelAngle)*dFrictionForce, 0); //always acts in direction opposed to velocity in DYNAMIC friction mode
		//alwyas acts in direction opposite to force in STATIC friction mode

		if (pSim->pEnv->getUsingStickyFloor())
		{
			Vel.x = 0; Vel.y = 0; LinMom.x = 0; LinMom.y = 0; StaticFricFlag = true; // nac: for transfer to reality == assume static friction if touching ground
		}

		if (Vel.x == 0 && Vel.y == 0){ //STATIC FRICTION: if this point is stopped and in the static friction mode...
			if (SurfaceForce < LocUStatic*NormalForce) StaticFricFlag = true; //if we don't have enough to break static friction
		}
		else { //DYNAMIC FRICTION
			if (dFrictionForce*pSim->dt < Mass*SurfaceVel){ //check momentum. if we are not possibly coming to a stop this timestep, add in the friction force
				FloorForce += FricForceToAdd;
			}
			else { //if we are coming to a stop, don't overshoot the stop. Set to zero and zero the momentum to get static friction to kick in.
				StaticFricFlag = true;
				LinMom.x = 0; //fully stop the voxel here! (caution...)
				LinMom.y = 0;
			}
		}

	}
	return FloorForce;

}

Vec3D<> CVXS_Voxel::CalcGndDampEffect() //damps everything to ground as quick as possible...
{
	vfloat tmp = 0;
//	for (int i=0; i<GetNumLocalBonds(); i++) tmp+=sqrt(GetBond(i)->GetLinearStiffness()*Mass);
	for (int i=0; i<6; i++) tmp+=sqrt(InternalBondPointers[i]->GetLinearStiffness()*Mass);

	return -pSim->GetSlowDampZ()*2*tmp*Vel;
}


vfloat CVXS_Voxel::GetMaxBondStrain(void) const
{
	vfloat MxSt = 0;
	for (int i=0; i<6; i++){
		if (InternalBondPointers[i] != NULL){
			vfloat TSt = InternalBondPointers[i]->GetEngStrain();
			if (TSt>MxSt) MxSt = TSt;
		}
	}
	return MxSt;
}

vfloat CVXS_Voxel::GetMaxBondStrainE(void) const
{
	vfloat MxSt = 0;
	for (int i=0; i<6; i++){
		if (InternalBondPointers[i] != NULL){
			vfloat TSt = InternalBondPointers[i]->GetStrainEnergy();
			if (TSt>MxSt) MxSt = TSt;
		}
	}
	return MxSt;
}

vfloat CVXS_Voxel::GetMaxBondStress(void) const
{
	vfloat MxSt = 0;
//	for (int i=0; i<NumLocalBonds; i++){
	for (int i=0; i<6; i++){
		if (InternalBondPointers[i] != NULL){
			vfloat TSt = InternalBondPointers[i]->GetEngStress();
			if (TSt>MxSt) MxSt = TSt;
		}
	}
	return MxSt;
}

vfloat CVXS_Voxel::GetAvgBondStress(void) const
{
	vfloat AvgStress = 0;
//	for (int i=0; i<NumLocalBonds; i++){
	for (int i=0; i<6; i++)
		if (InternalBondPointers[i] != NULL)
			AvgStress += (InternalBondPointers[i]->GetEngStress()/6);

	return AvgStress;
}

vfloat CVXS_Voxel::GetNeighborhoodAvgBondStress(void)
{
	int numNearby = NumNearbyVox();
	vfloat neighborsAvgStress = 0.0;
	for(int idN = 0; idN < numNearby; idN ++)
		neighborsAvgStress += pSim->VoxArray[NearbyVoxInds[idN]].GetAvgBondStress()/(numNearby+1);

	neighborsAvgStress += GetAvgBondStress()/(numNearby+1); // Also consider this voxel in the computation

	return neighborsAvgStress;
}


vfloat CVXS_Voxel::CalcVoxMatStress(const vfloat StrainIn, bool* const IsPastYielded, bool* const IsPastFail) const
{
		return _pMat->GetModelStress(StrainIn, IsPastYielded, IsPastFail);
}
