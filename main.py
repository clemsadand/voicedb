from utils.tools import get_intent, execute_command
from utils.utils import transcribe_audio


if __name__ == "__main__":
	import argparse

	#setup a parser to get file
	parser = argparse.ArgumentParser(description="A simple program that greets a user.")
	parser.add_argument("filename", default="dev_audio/row4.flac", help="The command audio file to use")
	args = parser.parse_args()
	filename = args.filename
	
	# transcribe the audio
	command = transcribe_audio(filename)
	cmd_to_db = get_intent(command)
	
	print()
	print(cmd_to_db)
	
	#print(execute_command(cmd_to_db))

