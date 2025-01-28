#include <stdlib.h>
#include <dicom/dicom.h>

int main() {
    const char *file_path = "/path/to/file.dcm";
    DcmError *error = NULL;

    DcmFilehandle *filehandle = dcm_filehandle_create_from_file(&error, file_path);
    if (filehandle == NULL) {
        dcm_error_log(error);
        dcm_error_clear(&error);
        return 1;
    }

    const DcmDataSet *metadata =
        dcm_filehandle_get_metadata_subset(&error, filehandle);
    if (metadata == NULL) {
        dcm_error_log(error);
        dcm_error_clear(&error);
        dcm_filehandle_destroy(filehandle);
        return 1;
    }

    const char *num_frames;
    uint32_t tag = dcm_dict_tag_from_keyword("NumberOfFrames");
    DcmElement *element = dcm_dataset_get(&error, metadata, tag);
    if (element == NULL ||
        !dcm_element_get_value_string(&error, element, 0, &num_frames)) {
        dcm_error_log(error);
        dcm_error_clear(&error);
        dcm_filehandle_destroy(filehandle);
        return 1;
    }

    printf("NumerOfFrames == %s\n", num_frames);

    dcm_filehandle_destroy(filehandle);

    return 0;
}
