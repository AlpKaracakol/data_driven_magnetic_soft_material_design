/*******************************************************************************
Copyright (c) 2010, Jonathan Hiller (Cornell University)
If used in publication cite "J. Hiller and H. Lipson "Dynamic Simulation of Soft Heterogeneous Objects" In press. (2011)"

This file is part of Voxelyze.
Voxelyze is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Voxelyze is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
See <http://www.opensource.org/licenses/lgpl-3.0.html> for license details.
*******************************************************************************/

#ifndef VXS_VOXEL_H
#define VXS_VOXEL_H

#include "VX_Voxel.h"
#include "Utils/Vec3D.h"
#include "Utils/Quat3D.h"
#include <math.h>

class CVXS_BondCollision;


//http://gafferongames.com/game-physics/physics-in-3d/

//info about a voxel that changes during a simulation (i.e. state)
class CVXS_Voxel : public CVX_Voxel
{
public:
	CVXS_Voxel(CVX_Sim* pSimIn, int SIndexIn, int XIndexIn, int MatIndexIn, Vec3D<>& NominalPositionIn, vfloat OriginalScaleIn, bool trackThisVoxelIn = false);
	~CVXS_Voxel(void);
	CVXS_Voxel(const CVXS_Voxel& VIn) : CVX_Voxel(VIn) {*this = VIn;} //copy constructor
	CVXS_Voxel& operator=(const CVXS_Voxel& VIn);

	void ResetVoxel(); //resets this voxel to its default (imported) state.

	void EulerStep(); //updates the state of the voxel based on the current forces and moments.

	// get info about the magnetization of this voxel
	inline Vec3D<> GetInitMDirec() const {return M_DirecInit;}
	inline vfloat GetCurMMagnitude() const {return M_Magnitude;}
	inline Vec3D<> GetCurMDirec() const {return M_DirecCur;}
	inline Vec3D<> GetCurMoment() const {return m_MomentCur;}

	// Set info about the magnetization of this voxel
	inline void SetInitMDirec(const Vec3D<>& M_DirecInitIn) {M_DirecInit = M_DirecInitIn;}
	inline void SetCurMMagnitude(const vfloat& M_MagnitudeIn) {M_Magnitude = M_MagnitudeIn;}
	inline void SetCurMDirec(const Vec3D<>& M_DirecCurIn) {M_DirecCur = M_DirecCurIn;}
	inline void SetCurMoment(const Vec3D<>& m_MomentCurIn) {m_MomentCur = m_MomentCurIn;}

	// external B field
	inline Vec3D<> GetCurBExt() const {return B_Ext;}
	inline void SetCurBExt(const Vec3D<>& B_ExtIn) {B_Ext = B_ExtIn;}
	inline Vec3D<> GetCurBGradExt() const {return Bgrad_Ext;}
	inline void SetCurBGradExt(const Vec3D<>& Bgrad_ExtIn) {Bgrad_Ext = Bgrad_ExtIn;}

	// external disturbance force
	inline Vec3D<> GetFExtDist() const {return F_Ext_Dist;}
	inline void SetFExtDist(const Vec3D<>& F_Ext_DistIn) {F_Ext_Dist = F_Ext_DistIn;}
	
	//Collisions
	bool LinkColBond(int CBondIndex); //collision bond index...
	void UpdateColBondPointers(); //updates all links (pointers) to bonds according top current p_Sim
	void UnlinkColBonds();

	//input information
	inline void SetInputForce(const Vec3D<>& InputForceIn) {InputForce = InputForceIn;} //adds a specified force to this voxel. Subsequent calls over-write this force. (Can be used in conjunction with picking in gui to drag voxels around)
	inline void ScaleExternalInputs(const vfloat ScaleFactor=1.0) {ExternalInputScale=ScaleFactor;} //scales force, torque, etc. to some percentage of its set value

	//Get info about the current state of this voxel
	const inline Vec3D<> GetCurPos() const {return Pos;}
	const inline Vec3D<double> GetCurPosHighAccuracy(void) const {return Pos;}
	const inline Quat3D<> GetCurAngle() const {return Angle;}
	const inline Quat3D<double> GetCurAngleHighAccuracy(void) const {return Angle;}
	const inline vfloat GetCurScale() const {return Scale;}
	const inline Vec3D<> GetCurVel() const {return Vel;}
	const inline Vec3D<> GetCurAngVel() const {return AngVel;}
	const inline vfloat GetPressure() const {return Pressure;}
	const inline vfloat GetCurKineticE() const {return KineticEnergy;}
	const inline bool GetCurStaticFric() const {return StaticFricFlag;}
	const inline vfloat GetCurAbsDisp() const {return (Vec3D<>(Pos)-GetNominalPosition()).Length();}
	inline Vec3D<> GetSizeCurrent() const {return CornerPosCur-CornerNegCur;}
	inline Vec3D<> GetCornerPos() const {return CornerPosCur;}
	inline Vec3D<> GetCornerNeg() const {return CornerNegCur;}

	vfloat GetMaxBondStrain() const;
	vfloat GetMaxBondStrainE() const;
	vfloat GetMaxBondStress() const;
	vfloat GetAvgBondStress() const;
	vfloat GetNeighborhoodAvgBondStress();


	vfloat GetCurGroundPenetration(); //how far into the ground penetrating (penetration is positive, no penetration is zero)
	Vec3D<> GetCurForce(bool forceRecalc = false) {if (forceRecalc) CalcTotalForce(); return ForceCurrent;} //just returns last calculated force

	//yeilded and broken flags
	inline void SetYielded(const bool Yielded) {VYielded = Yielded;}
	inline bool GetYielded() const {return VYielded;}
	inline void SetBroken(const bool Broken) {VBroken = Broken;}
	inline bool GetBroken() const {return VBroken;}

	//utilities
	inline void ZeroMotion() {LinMom = Vec3D<double>(0,0,0); AngMom = Vec3D<double>(0,0,0); Vel = Vec3D<>(0,0,0); AngVel = Vec3D<>(0,0,0); KineticEnergy = 0;}
	vfloat CalcVoxMatStress(const vfloat StrainIn, bool* const IsPastYielded, bool* const IsPastFail) const;

	//display color stuff
	void SetColor(float r, float g, float b, float a);

	//Poissons!
	void SetStrainDir(BondDir Bond, vfloat StrainIn);
	Vec3D<> StrainPosDirsCur, StrainNegDirsCur; //cache the strain in each bond direction
	vfloat GetVoxelStrain(Axis DesiredAxis);

	bool inRing;
	bool oldInRing;

	float phaseOffset;
	float finalPhaseOffset;
	float TempAmpDamp;
	float finalTempAmpDamp;
	float growthTime;
	float startGrowthTime;
	float finalVoxelSize;
	float OriginalFinalVoxelSize;
	float initialVoxelSize;
	float RemainingGrowth;
	float CurPhaseChange;
	float onsetBound;
	float terminationBound;
	float evolvedStiffness;
	float stiffnessPlasticityRate;
	float KP;
	float KI;
	float ANTIWINDUP;
	float TempAmplitude;
	float TempPeriod;

	double getCurrentStimulus(){ return currentStimulus; } // FC: stimulus from environmental sources
	double getCurrentTempFact(){ return TempFact; }
	//void initLastTempFact(double t){lastTempFact = t; }
	void setVoxelScale(double s) { Scale = s;  } //lastTempFact = Scale/GetNominalSize();
	Vec3D<double> getVoxPointingVector(){ return voxPointingVector; }
	Vec3D<double> getDesiredPointingVector(){ return desiredPointingVector; }
	double getIntegralComponent(){ return integralComponent; }

	double getCurScaleVariation(){ return fabs((initialVoxelSize - Scale)/initialVoxelSize)*100; }


	bool IsExtDistF = 0;


private:

	// magnetic variables
	Vec3D<double> M_DirecInit;
	Vec3D<double> M_DirecCur;
	vfloat M_Magnitude;  // TODO: --> check here, could be done in material section later @alp
	Vec3D<double> m_MomentCur;
	vfloat M_PerVol;

  	Vec3D<double> B_Ext;
	Vec3D<double> Bgrad_Ext;
	Vec3D<double> F_Ext_Dist;


	//State variable of this voxel being simulated
	Vec3D<double> Pos; //translation
	Vec3D<double> LinMom;
	Quat3D<double> Angle; //rotation
	Vec3D<double> AngMom;
	vfloat Scale; //nominal scale based on temperature, etc.
	Vec3D<> CornerPosCur, CornerNegCur; //actual size based on volume effects or other deviations from Scale
	bool StaticFricFlag; //flag to set if this voxel shouldnot move in X/Y due to being in static friction regime
	bool VYielded, VBroken; //is this voxel yielded or brokem according to the current material model?

	//convenience derived secondary state quantities:
	Vec3D<> Vel;
	vfloat KineticEnergy;
	Vec3D<> AngVel;
	vfloat Pressure;

	//current input parameters
	vfloat ExternalInputScale; //Scales the external Force, displacement, torque (range: 0-1)
	Vec3D<> InputForce; //current input force (general purpose force acting on this voxel)

	//collision system information
	std::vector<int> ColBondInds; //collision bond indices
	std::vector<CVXS_BondCollision*> ColBondPointers; //collision bond pointers
	inline bool IAmVox2Col(const int BondDirColIndex) const; //returns true if this voxel is Vox2 of the specified bond

	//current display color of this voxel.
	float m_Red, m_Green, m_Blue, m_Trans; //can update voxel color based on state, mode, etc.

	//force calculations of this voxel
	Vec3D<> ForceCurrent; //cached current force, as last calculated by CalcTotalForce()

	Vec3D<> CalcTotalForce(); //calculates the total force acting on this voxel (without fixed constraints...)
	Vec3D<> CalcTotalMoment(); //Calculates the total moment action on this voxel

	//secondary force calculations
	Vec3D<> CalcFloorEffect(Vec3D<> TotalVoxForce); //calculates the object's interaction with a floor under gravity
	Vec3D<> CalcGndDampEffect(); //damps everything to ground as quick as possible...

	vfloat lastTempFact;
	vfloat lastScale;
	vfloat TempFact;
	std::vector<VX_Source*> environmentalSources;
	double maxNormDistanceFromSource = 0.0;
	bool firstStep = 1;
	double currentStimulus;

	double SuggestedFinalVoxelSize;

	Vec3D<double> initialVoxPointingVector;
	Vec3D<double> voxPointingVector;
	Vec3D<double> targetPosition;
	Vec3D<double> desiredPointingVector;
	double voxPointingError;
	double integralComponent;
};

#endif //VXS_VOXEL_H
