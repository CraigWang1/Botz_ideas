const bool GMAN = true;

Observation VisionService::findGateML(cv::Mat img)
{
	ROS_INFO("Starting machine learning detection for GATE.");
		
	log(img, 'f');
	
	//Preprocess the image and place the filter
	cv::Mat temp;
	cv::Mat inp;
	img.copyTo(temp);
	cv::cvtColor(img, inp, CV_BGR2RGB);
	std::vector<float> img_data;
	preprocess(inp,img_data,maxdim);
	
	auto inpName = new Tensor(model, "input_1");
	auto out_boxes = new Tensor(model, "filtered_detections/map/TensorArrayStack/TensorArrayGatherV3");
	auto out_scores = new Tensor(model, "filtered_detections/map/TensorArrayStack_1/TensorArrayGatherV3");
	auto out_labels = new Tensor(model, "filtered_detections/map/TensorArrayStack_2/TensorArrayGatherV3");
	
	// Put image in tensor.
	inpName->set_data(img_data, { 1, maxdim, maxdim, 3 });

	model.run(inpName, { out_boxes, out_scores, out_labels });
	// Store output in variables so don't have to keep calling get_data()
	auto boxes = out_boxes->get_data<float>();
	auto scores = out_scores->get_data<float>();
	auto labels = out_labels->get_data<int>();
	// Visualize detected bounding boxes.

	float gate_x, gate_y, gate_right, gate_bottom, gman_x, pic2_x;

	for (int i = 0; i < scores.size(); i++) 
	{

		int class_id = labels[i];
		float score = scores[i];
		std::vector<float> bbox = { boxes[i*4], boxes[i*4+1], 
			boxes[i*4+2], boxes[i*4+3] };
		if (score > 0.5) 
		{
			float x = bbox[0];
			float y = bbox[1];
			float right = bbox[2];
			float bottom = bbox[3];
			if (class_id == 0)
			{
				ROS_INFO("Gate found");
				gate_x = x;
				gate_y = y;
				gate_right = right;
				gate_bottom = bottom;
			}
			else if (class_id == 1)
			{
				ROS_INFO("Gman picture found");
				gman_x = x;

			}
			else if (class_id == 2)
			{
				ROS_INFO("Pic 2 found");
				pic2_x = x;
			}
			if (gate_x && (gman_x || pic2_x))
				break;
		}
		else break;
	}

	if (gate_x)
	{
		if (gman_x || pic2_x)
			ROS_INFO("Found path");
		else
			ROS_INFO("Guessing path");
		cv::rectangle(temp, {(int)x, (int)y}, {(int)right, (int)bottom}, 
				{255, 0, 255}, 5);
		//log(temp, 'e');

		// Calculate position to pass through on left or right side of gate
		float target_x;
		float target_y;
		float gate_width = std::fabs(gate_right - gate_x);
		float gate_height = std::fabs(gate_bottom - gate_y);
		float x_offset = (float)gate_width * 0.25;
		float y_offset = (float)gate_height * 0.4;

		// Fix this, it was meant to read from mission config.hpp but it caused errors during catkin make
		// Because vision is built before mission

		// Worst case if we can't detect the pictures, then the code will just guess
		bool GMAN_LEFT = true;
		bool GATE_LEFT;
		float gate_center_x = (gate_x + gate_right) / 2.;
		if (gman_x)
		{
			if (gman_x < gate_center_x)
				GMAN_LEFT = true;
			else
				GMAN_LEFT = false;
		}
		else if (pic2_x)
		{
			if (pic2_x < gate_center_x)
				GMAN_LEFT = false;
			else
				GMAN_LEFT = true;
		}
		if (GMAN_LEFT && GMAN)
			GATE_LEFT = true;
		else if (!GMAN_LEFT && !GMAN)
			GATE_LEFT = true;
		else
			GATE_LEFT = false;

		if (GATE_LEFT) 
			target_x = gate_center_x - x_offset;
		else 
			target_x = gate_center_x + x_offset;
		target_y = gate_bottom - y_offset;

		cv::circle(temp, cv::Point((int)target_x, (int)target_y), 10, {255, 0, 255}, cv::FILLED);
		log(temp, 'e');

		// Calculate distance based on camera parameters 
		float det_height = std::fabs(gate_bottom - gate_y);
		float det_width = std::fabs(gate_right - gate_x);
		float dist = calcDistance(8, 1524, FIMG_DIM_RES[0], det_height, 8.8);

		return Observation(score, target_y, target_x, dist);
	}

	return Observation(0, 0, 0, 0);
}