from pypdf import PdfReader


def extract_resume_text(pdf_path):

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


if __name__ == "__main__":

    print("=" * 60)
    print("RESUME PDF TEXT EXTRACTION")
    print("=" * 60)

    pdf_path = input(
        "\nEnter the path of your resume PDF: "
    )

    resume_text = extract_resume_text(pdf_path)

    print("\nResume Text:")
    print("-" * 60)

    print(resume_text)

    print("-" * 60)

    print(
        "\nTotal Characters:",
        len(resume_text)
    )

    print("\nResume parsing completed.")
