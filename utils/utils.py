from gtts import gTTS
import whisper

model = whisper.load_model("base")

def transcribe_audio(filepath, lang="en"):
	
	end = filepath.split(".")[-1]
	
	result = model.transcribe(
		filepath, 
		language=lang, 
		task="transcribe"
	)
	
	#output = filepath[:-len(end)-1] + ".txt"
	#with open(output, "w") as f:
	#	f.write(result["text"])
	
	return result["text"]

def convert_to_audio(text, outpath):
	tts = gTTS(text, lang="en", tld="com")
	tts.save(outpath)



if __name__ == "__main__":
	"""
	transcribe_audio("../speech1.flac")
	transcribe_audio("../speech2.flac")
	transcribe_audio("../speech3.flac", "fr")
	"""
	
	with open("test.csv", "r") as f:
		tests = f.readlines()
	for i, test in enumerate(tests):
		convert_to_audio(test, f"test/{i}.mp3")
		
