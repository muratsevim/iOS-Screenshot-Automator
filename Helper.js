function captureLocalizedScreenshot(prefix, name) 
{
	var target = UIATarget.localTarget();
	var model = target.model();
	var rect = target.rect();
	
	if (model.match(/iPhone/)) 
	{
		if (rect.size.height > 480) model = "iphone5";
		else model = "iphone";
	} 
	else 
	{
		model = "ipad";
  	}

	var orientationName = "portrait";
	if (rect.size.height < rect.size.width) orientationName = "landscape";
	
	var language = target.frontMostApp().preferencesValueForKey("AppleLanguages")[0];
	
	var parts = [language, model, name];
	
	var imageName = prefix + parts.join("-");
	//using application frame to generate screenshots without the status bar.
	var application = target.frontMostApp();
	var applicationFrame = application.rect();
	target.captureRectWithName(applicationFrame, imageName);
	//target.captureScreenWithName(imageName);
}