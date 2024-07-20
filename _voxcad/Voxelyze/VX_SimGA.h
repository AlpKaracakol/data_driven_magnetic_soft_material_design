/*******************************************************************************
Copyright (c) 2010, Jonathan Hiller (Cornell University)
If used in publication cite "J. Hiller and H. Lipson "Dynamic Simulation of Soft Heterogeneous Objects" In press. (2011)"

This file is part of Voxelyze.
Voxelyze is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Voxelyze is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
See <http://www.opensource.org/licenses/lgpl-3.0.html> for license details.
*******************************************************************************/

#ifndef VX_SIMGA_H
#define VX_SIMGA_H

//wrapper class for VX_Sim with convenience functions and nomenclature for using Voxelyze within a genetic algorithm.

#include <limits> // numeric limits (allows to define a Inf value, which may come in handy)
#include "VX_Sim.h"

enum FitnessTypes{FT_NONE, FT_CENTER_MASS_DIST, FT_VOXEL_DIST};
class CVX_SimGA : public CVX_Sim
{

public:
	CVX_SimGA();
	~CVX_SimGA(){};

	void SaveResultFile(std::string filename);
	void WriteResultFile(CXML_Rip* pXML);

	void WriteAdditionalSimXML(CXML_Rip* pXML);
	bool ReadAdditionalSimXML(CXML_Rip* pXML, std::string* RetMessage = NULL);

	float Fitness;	//!<Keeps track of whatever fitness we choose to track
	FitnessTypes FitnessType; //!<Holds the fitness reporting type. For now =0 tracks the center of mass, =1 tracks a particular Voxel number
	int	TrackVoxel;		//!<Holds the particular voxel that will be tracked (if used).
	std::string FitnessFileName;	//!<Holds the filename of the fitness output file that might be used
	bool WriteFitnessFile;
	//	bool print_scrn;	//!<flags whether status will be sent to the console



	// magnetic cases
	/* saving options for the simulator */
	bool isSavePosition = true;
	bool isSaveOrientation = false;
	bool isSaveVelocity = false;
	bool isSaveAngVel = false;
	bool isSaveStrainEnergy = true;
	bool isSaveKineticEnergy = false;
	bool isSavePressure = false;
	bool isSaveForce = false;


	/* special demo cases for the */
	bool isCaseMaxCOMZPos = false;
	bool isCaseMaxMinPosZ = false;
	Vec3D<double> COM_maxZ = Vec3D<>(0,0,0);
	Vec3D<double> COMvel_maxVelZ = Vec3D<>(0,0,0);
	Vec3D<double> MaxMinPosZ = Vec3D<>(0,0,0);

	Vec3D<double> Fext_at_limit = Vec3D<>(0.,0.,0.);
	int	minVoxNum_touchingFloor = 99999;

	int sampleAirTotStep = 0;
	float sampleAirTotTime = 0.0;
	bool isSampleOnAir = false;

	bool isDemo3D = false;

	std::vector<double> walkerCOMXs;

};

#endif //VX_SIMGA_H
